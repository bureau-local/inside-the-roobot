import json
import csv

# Lookup to match the deliveroo working zones to cities
with open("data/in/zone-city-lookup.csv") as infile:
	reader = csv.DictReader(infile)
	fields = reader.fieldnames
	zones_lookup = {row["Zone"]: row["City"] for row in reader}
	cities = {zones_lookup[zone] for zone in zones_lookup}

# Lookup to match the free text entries to cities
with open("data/in/area-city-lookup.csv") as infile:
	reader = csv.DictReader(infile)
	fields = reader.fieldnames
	areas_lookup = {row["Area"]: row["City"] for row in reader}
	second_cities_set = {areas_lookup[area] for area in areas_lookup}
	cities.update(second_cities_set)

# geo-cleaning zones and matching/cleaning cities
with open("data/tmp/iwgb-data-1.json", "r") as infile:
	iwgb_data = json.load(infile)

	for invoice in iwgb_data:
		zone = invoice["zone"]	
		
		if zone.upper() in zones_lookup:
			zone = zone.upper()
			city = zones_lookup[zone]
		elif zone.title() in cities:
			zone = zone.title()
			city = zone.title()
		elif zone.title() in areas_lookup:
			zone = zone.title()
			city = areas_lookup[zone]
		else:
			city = ""

		invoice["zone"] = zone
		invoice["city"] = city

with open('data/tmp/iwgb-data-2.json', 'w') as outfile:
    json.dump(iwgb_data, outfile)
