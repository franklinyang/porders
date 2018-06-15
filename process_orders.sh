#!/bin/bash
rm turk_data/output.csv
echo Downloading new orders...
python turk_order_processing.py download 
echo Starting localturk...
localturk turk_order_processing.html turk_data/unprocessed_orders.csv turk_data/output.csv
echo Uploading orders...
python turk_order_processing.py upload
