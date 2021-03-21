from datetime import date
import json
import csv

# Lookup between riders deduplicated ids and original ids
with open("data/in/duplicated-pairs.csv") as infile:
	reader = csv.DictReader(infile)
	fields = reader.fieldnames
	dedup_lookup = {row["Duplicate Id"]: row["Original Id"] for row in reader}

# get infile name from date and write data to file
filename_date = date.today().strftime("%Y%m%d")
infile_name = "iwgb-data-{}.json".format(filename_date)
infile_path = "data/in/iwgb/" + infile_name 
with open(infile_path, "r") as infile:
	iwgb_data = json.load(infile)
	# dedup rider ids
	for invoice in iwgb_data:
		rider_id = invoice["riderId"]
		if rider_id in dedup_lookup:
			invoice["riderId"] = dedup_lookup[rider_id]

with open('data/tmp/iwgb-data-1.json', 'w') as outfile:
    json.dump(iwgb_data, outfile)
