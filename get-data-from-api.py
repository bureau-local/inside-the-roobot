from dotenv import load_dotenv
from datetime import date
import requests
import json
import sys
import os

# check if the invoice was succesfully parsed by IWGB's tool,
# and if it isn't test data - that wouldn't have been submitted by riders
# @param invoice: dict
def is_a_valid_invoice(invoice):
	if invoice["status"] == "success" and invoice["zone"] != "TEST_DATA":
		return True
	else:
		return False
 
url = "https://internal.iwgb.org.uk/roovolt/api/data"
# load contents of our .env file
# accessible as a Map with .get()
load_dotenv()
key = os.getenv("IWGB_API_KEY")
if key == None:
	sys.exit("[!] API key not set")
headers = {"Authorization": key}

r = requests.get(url, headers=headers)
if r.ok:
	iwgb_data = r.json()
	valid_invoices = [x for x in iwgb_data if is_a_valid_invoice(x)]

# get outfile name from date and write data to file
filename_date = date.today().strftime("%Y%m%d")
outfile_name = "iwgb-data-{}.json".format(filename_date)
outfile_path = "data/in/iwgb/" + outfile_name 
with open(outfile_path, 'w') as outfile:
    json.dump(valid_invoices, outfile)
