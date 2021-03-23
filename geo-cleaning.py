import json
import csv

# get the city and region corresponding to the geographic area
# @params geo_data: dict
def get_lookup(geo_data):
	return {"city": geo_data["City"], "region": geo_data["Region"]}

# get manual corrections for special cases
# @params row: dict
def get_correction(row):
	return {"area": row["Area"], "correction": row["Correction"]}

# Lookup to match the deliveroo working zones to cities
with open("data/in/corrections.csv") as infile:
	reader = csv.DictReader(infile)
	fields = reader.fieldnames
	corrections = {row["Rider Id"]: get_correction(row) for row in reader}

# Lookup to match the deliveroo working zones to cities
with open("data/in/zone-lookup.csv") as infile:
	reader = csv.DictReader(infile)
	fields = reader.fieldnames
	zones_lookup = {row["Zone"]: get_lookup(row) for row in reader}
	cities = {v["city"]: v["region"] for (k, v) in zones_lookup.items()}

# Lookup to match the free text entries to cities
with open("data/in/area-lookup.csv") as infile:
	reader = csv.DictReader(infile)
	fields = reader.fieldnames
	areas_lookup = {row["Area"]: get_lookup(row) for row in reader}
	more_cities = {areas_lookup[area]["city"] for area in areas_lookup}
	more_cities = {v["city"]: v["region"] for (k, v) in areas_lookup.items()}
	cities.update(more_cities)

# geo-cleaning zones and matching/cleaning cities
with open("data/tmp/iwgb-data-1.json", "r") as infile:
	iwgb_data = json.load(infile)

	for invoice in iwgb_data:
		rider_id = invoice["riderId"]
		zone = invoice["zone"]

		if rider_id in corrections and zone == corrections[rider_id]["area"]:
			zone = corrections[rider_id]["correction"]
		
		if zone.upper() in zones_lookup:
			zone = zone.upper()
			city = zones_lookup[zone]["city"]
			region = zones_lookup[zone]["region"]
		elif zone.title() in cities:
			zone = zone.title()
			city = zone.title()
			region = cities[zone]
		elif zone.title() in areas_lookup:
			zone = zone.title()
			city = areas_lookup[zone]["city"]
			region = areas_lookup[zone]["region"]
		else:
			city = ""
			region = ""

		invoice["zone"] = zone
		invoice["city"] = city
		invoice["region"] = region

with open('data/tmp/iwgb-data-2.json', 'w') as outfile:
    json.dump(iwgb_data, outfile)
