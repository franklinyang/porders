import csv
from datetime import datetime
import json
import os
import sys

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import requests

from create_orders import Order

SHOPIFY_HOST = "https://pinatas.myshopify.com"
TURK_INPUT_CSV_PATH = 'turk_data/unprocessed_orders.csv'
TURK_OUTPUT_CSV_PATH = 'turk_data/output.csv'
SERVICE_CREDENTIALS_PATH = os.path.expanduser('~/Dropbox/Solid Internet Properties/sheets_api_creds.json')
SHOPIFY_CREDS_PATH = os.path.expanduser('~/Dropbox/Solid Internet Properties/shopify_api_creds.json')
with open(SHOPIFY_CREDS_PATH, 'r') as f:
    SHOPIFY_CREDS = json.load(f)


# Shopify API Calls
def get_latest_orders():
    orders = "/admin/orders.json?"
    unshipped = "fulfillment_status=unshipped"
    id_cutoff = "since_id=508081307766"

    response = requests.get(SHOPIFY_HOST + orders + id_cutoff + "&" + unshipped,
                            auth=(SHOPIFY_CREDS["API_KEY"],
                                  SHOPIFY_CREDS["API_PASSWORD"]))
    orders = json.loads(response.text)["orders"]
    return orders
    

def get_product_img(product_id):
    product_img_url = "/admin/products/" + str(product_id) + "/images.json"
    response = requests.get(SHOPIFY_HOST + product_img_url,
                            auth=(SHOPIFY_CREDS["API_KEY"],
                                  SHOPIFY_CREDS["API_PASSWORD"]))
    prod = json.loads(response.text)["images"]
    if len(prod) > 0:
        return prod[0]["src"]
    else:
        return None


def get_product(product_id):
    product_img_url = "/admin/products/" + str(product_id) + ".json"
    response = requests.get(SHOPIFY_HOST + product_img_url,
                            auth=(SHOPIFY_CREDS["API_KEY"],
                                  SHOPIFY_CREDS["API_PASSWORD"]))
    prod = json.loads(response.text)["product"]
    return prod


def process_order_turk(order):
    order_obj = {}
    shipping_addr = order["shipping_address"]
    order_obj["shipping_city"] = shipping_addr["city"]
    order_obj["shipping_state"] = shipping_addr["province"]
    order_obj["shipping_zip"] = shipping_addr["zip"]
    order_obj["additional_notes"] = order["note"].replace("\r\n", " <NEW_LINE> ").encode('utf-8')
    for note_attr in order["note_attributes"]:
        if note_attr["name"] == "date":
            order_obj["party_date_parsed"] = note_attr["value"]

    # get img paths
    for item in order["line_items"]:
        img = get_product_img(item["product_id"])
        item["img"] = img if img else ""

    order_obj["items"] = json.dumps(order["line_items"]).replace("\r\n", " <NEW_LINE> ").encode('utf-8')
    return order_obj


def write_orders_to_csv(orders, path):
    processed_orders = [process_order_turk(order) for order in orders]
    fieldnames = processed_orders[0].keys()
    with open(path, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_orders)


# Google Sheets Interactions
def get_orders_sheet():
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_CREDENTIALS_PATH, scope)
    client = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open("Pinata Invoices").sheet1
    return sheet


def get_next_row_idx(sheet):
    col_vals = sheet.col_values(1)
    for (i, val) in enumerate(reversed(col_vals)):
        if val == '':
            pass
        else:
            break
    return len(col_vals[:-1*i]) + 1


def write_order_to_sheets(sheet, order):
    cells = [
        (1, datetime.today().strftime("%m/%d/%Y")) # Today
        , (2, order.qty) # Qty
        , (3, order.pinata) # Pinata
        , (4, 1 if order.busters == "YES" else 0) # Buster
        , (5, 1 if order.blindfolds == "YES" else 0) # Blindfold
        , (6, 1 if order.pullstrings == "YES" else 0) # Pullstring
        , (7, 1 if order.rushed == "YES" else 0) # Rushed
        , (8, 1 if order.pictures == "YES" else 0) # Pictures
        , (9, order.size) # Size
        , (10, order.notes) # Notes
        , (12, order.ship_by) # Ship By
        , (13, order.party_date) # Party Date        
    ]
    row_idx = get_next_row_idx(sheet)
    for (col, val) in cells:
        sheet.update_cell(row_idx,col,str(val))


def write_processed_orders(path):
    sheet = get_orders_sheet()
    turk_out = pd.read_csv(path)
    orders = []
    for (idx, dfrow) in turk_out.iterrows():
        row = dfrow.to_dict()
        row["ship_by"] = datetime.strptime(row["ship_by"], "%Y-%m-%d").strftime("%m/%d/%Y")
        row["party_date"] = datetime.strptime(row["party_date"], "%Y-%m-%d").strftime("%m/%d/%Y")
        row["notes"] = row["notes"].replace("<NEW_LINE>", "\n") if type(row["notes"]) == "str" else ""
        row["pictures"] = 0
        row["imgs"] = row["imgs"].split(",")
        order = Order(row)
        write_order_to_sheets(sheet, order)
        orders.append(order)
    return orders




if __name__ == '__main__':
    option = sys.argv[1]
    if option == "download":
        # Get latest orders
        orders = get_latest_orders()
        write_orders_to_csv(orders, TURK_INPUT_CSV_PATH)
    elif option == "upload":
        # Write orders to sheets and print email text
        orders = write_processed_orders(TURK_OUTPUT_CSV_PATH)
        for order in orders:
            order.print_order()
    else:
        raise Exception("Please input a valid option {download, upload}")
