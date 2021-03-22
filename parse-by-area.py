import json
import csv

# @params local_data: dict
# @params area: string
# @params city: string
# @params zone: string
def init_data(local_data, area, city, zone=""):
	local_data[area] = dict()
	if zone != "":
		local_data[area]["Zone"] = zone
	local_data[area]["City"] = city
	local_data[area]["Riders"] = set()
	local_data[area]["Invoices"] = 0
	local_data[area]["Shifts"] = 0
	local_data[area]["Orders"] = 0
	local_data[area]["Hours"] = 0
	local_data[area]["Pay"] = 0
	local_data[area]["Shifts < £10/h"] = 0
	local_data[area]["Shifts < min wage"] = 0

# @params local_data: dict
# @params area: string
# @params invoice: dict
def increment_data(local_data, area, invoice):
	local_data[area]["Riders"].add(invoice["riderId"])
	local_data[area]["Invoices"] += 1
	local_data[area]["Shifts"] += invoice["Number of shifts"]
	local_data[area]["Orders"] += invoice["Total orders"]
	local_data[area]["Hours"] += invoice["Hours"]
	local_data[area]["Pay"] += invoice["Total Pay"]
	local_data[area]["Shifts < £10/h"] += invoice["Shifts < £10/h"]
	local_data[area]["Shifts < min wage"] += invoice["Shifts < min wage"]

# @params local_data: dict
def analyse_data(local_data):
	shifts = local_data["Shifts"]
	orders = local_data["Orders"]
	hours = local_data["Hours"]
	pay = local_data["Pay"]
	shifts_below_ten = local_data["Shifts < £10/h"]
	shifts_below_min = local_data["Shifts < min wage"]
	shifts_below_ten_percentage = round(shifts_below_ten / shifts, 4)
	shifts_below_min_percentage = round(shifts_below_min / shifts, 4)

	local_data["Hours"] = round(hours, 1)
	local_data["Riders"] = len(local_data["Riders"])
	local_data["Orders per hour"] = round(orders / hours, 3)
	local_data["Shifts < £10/h (%)"] = shifts_below_ten_percentage
	local_data["Shifts < min wage (%)"] = shifts_below_min_percentage
	local_data["Hourly pay"] = round(pay / hours, 2)

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
	analyse_data(zones_data[zone])

for city in cities_data:
	analyse_data(cities_data[city])

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
