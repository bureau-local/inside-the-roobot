import json
import csv

def init_data(geo_dict, area, city, zone=""):
	geo_dict[area] = dict()
	if zone != "":
		geo_dict[area]["Zone"] = zone
	geo_dict[area]["City"] = city
	geo_dict[area]["Riders"] = set()
	geo_dict[area]["Invoices"] = 0
	geo_dict[area]["Shifts"] = 0
	geo_dict[area]["Hours"] = 0
	geo_dict[area]["Pay"] = 0
	geo_dict[area]["Shifts < min wage"] = 0

def increment_data(geo_dict, area, invoice):
	geo_dict[area]["Riders"].add(invoice["riderId"])
	geo_dict[area]["Invoices"] += 1
	geo_dict[area]["Shifts"] += invoice["Number of shifts"]
	geo_dict[area]["Hours"] += invoice["Hours"]
	geo_dict[area]["Pay"] += invoice["Total Pay"]
	geo_dict[area]["Shifts < min wage"] += invoice["Shifts < min wage"]

zones_data = dict()
cities_data = dict()
# Loop though invoices to collect data by area and city
with open("data/tmp/iwgb-data-4.json", "r") as infile:
	iwgb_data = json.load(infile)
	for i, invoice in enumerate(iwgb_data):
		zone = invoice["zone"]
		city = invoice["city"]

		if zone not in zones_data:
			init_data(zones_data, zone, city, zone)

		increment_data(zones_data, zone, invoice)

		# Skip if no city could be matched to the area provided by the rider
		if city == "":
			continue

		if city not in cities_data:
			init_data(cities_data, city, city)

		increment_data(cities_data, city, invoice)

# Analyse the data collected by zone and city
for zone in zones_data:
	zone_data = zones_data[zone]
	shifts = zone_data["Shifts"]
	hours = zone_data["Hours"]
	pay = zone_data["Pay"]
	shifts_below_min = zone_data["Shifts < min wage"]
	shifts_below_min_percentage = round(shifts_below_min / shifts, 4)

	zone_data["Hours"] = round(hours, 1)
	zone_data["Riders"] = len(zone_data["Riders"])
	zone_data["Shifts < min wage (%)"] = shifts_below_min_percentage
	zone_data["Hourly pay"] = round(pay / hours, 2)
	zones_data[zone] = zone_data

for city in cities_data:
	city_data = cities_data[city]
	shifts = city_data["Shifts"]
	hours = city_data["Hours"]
	pay = city_data["Pay"]
	shifts_below_min = city_data["Shifts < min wage"]
	shifts_below_min_percentage = round(shifts_below_min / shifts, 4)

	city_data["Hours"] = round(hours, 1)
	city_data["Riders"] = len(city_data["Riders"])
	city_data["Shifts < min wage (%)"] = shifts_below_min_percentage
	city_data["Hourly pay"] = round(pay / hours, 2)
	cities_data[city] = city_data

# Write the zones data to output file
print("[*] Writing the zones data to output file")
zones_data = [val for key, val in zones_data.items()]
outfields = [datafield for datafield in zones_data[0]]
with open("data/out/zones-data.csv", "w") as outfile:
	writer = csv.DictWriter(outfile, fieldnames=outfields)
	writer.writeheader()
	writer.writerows(zones_data)

# Write the cities data to output file
print("[*] Writing the cities data to output file")
cities_data = [val for key, val in cities_data.items()]
outfields = [datafield for datafield in cities_data[0]]
with open("data/out/cities-data.csv", "w") as outfile:
	writer = csv.DictWriter(outfile, fieldnames=outfields)
	writer.writeheader()
	writer.writerows(cities_data)
