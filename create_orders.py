from collections import namedtuple
import csv
import sys


class Order(object):
    def __init__(self, row):
        self.qty = row['qty']
        self.pinata = row['pinata']
        self.size = row['size']
        self.notes = row['notes']
        self.ship_by = row['ship_by']

        row['busters'] = int(row['busters'])
        row['blindfolds'] = int(row['blindfolds'])
        row['pullstrings'] = int(row['pullstrings'])
        row['rushed'] = int(row['rushed'])
        row['pictures'] = int(row['pictures'])
        
        self.pullstrings = 'YES' if row['pullstrings'] > 0 else 'NO'
        self.rushed = 'YES' if row['rushed'] > 0 else 'NO'
        self.pictures = 'YES' if row['pictures'] > 0 else 'NO'

        if 'price' in row:
            self.price = row['price']
        else:
            self.price = self.get_order_price(row["qty"], row["busters"], row["blindfolds"], 
                                              row["pullstrings"], row["rushed"], row["pictures"])

        if row['busters'] == 0:
            self.busters = 'NO'
        elif row['busters'] == 1:
            self.busters = 'YES'
        elif row['busters'] > 1:
            self.busters = 'YES, ' + str(row['busters'])

        if row['blindfolds'] == 0:
            self.blindfolds = 'NO'
        elif row['blindfolds'] == 1:
            self.blindfolds = 'YES'
        elif row['blindfolds'] > 1:
            self.blindfolds = 'YES, ' + str(row['blindfolds'])

        self.party_date =  row['party_date'] if row['party_date'] else ''


    def get_order_price(self, qty, busters, blindfolds, pullstrings, rushed, pictures):
        return (qty * 24.50) + (busters + blindfolds + pullstrings) * 3 + pictures


    # Hi Blanca - Here is an order for:
    # 
    # PINATA(S):     (1) 
    # NOTES: 
    # PULL STRING:   NO
    # BOX SIZE:        48x24x12
    # SHIP BY:          DATE
    # BUSTER:           NO
    # BLINDFOLD:      NO
    # PICTURE:          NO
    # PRICE: PRICE
    # 
    # Thanks,
    # Franklin
    def print_order(self):
        print\
'''
Hi Blanca - Here is an order for:

PINATA(S): ({qty}) {pinata}
NOTES: {notes}
PULL STRING: {pullstrings}
BOX SIZE: {size}
SHIP BY: {ship_by} '- party date is: ' {party_date}
BUSTER: {busters}
BLINDFOLD: {blindfolds}
PICTURE: {pictures}
PRICE: {price}
'''.format(qty=self.qty,
           pinata=self.pinata,
           notes=self.notes,
           pullstrings=self.pullstrings,
           size=self.size,
           ship_by=self.ship_by,
           party_date=self.party_date,
           busters=self.busters,
           blindfolds=self.blindfolds,
           pictures=self.pictures,
           price=self.price)

class OrderGenerator(object):
    # 0 - Date to Blanca
    # 1 - Qty
    # 2 - Name of Pinata
    # 3 - Buster
    # 4 - Blindfolds
    # 5 - Pull String
    # 6 - Rushed?
    # 7 - Pictures
    # 8 - Size
    # 9 - Notes
    # 10 - Amount Owed
    # 11 - Ship By
    # 12 - Party Date
    @classmethod
    def get_orders(cls, filename):
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                new_order = Order(row)
                new_order.print_order()

if __name__ == '__main__':
    OrderGenerator.get_orders(sys.argv[1])
