from utils import write_csv_outfile
import json

def get_data_for_area(area_type, area):
	return [x for x in riders_202021_data if x[area_type] == area]

def get_data_for_financial_year(riders_yearly_data):
	return [x for x in riders_yearly_data if x["financial year"] == "2020-21"]

# @params local_data: dict
# @params area: string
# @params area: region
# @params city: string
# @params zone: string
def init_data(local_data, area, region, city="", zone=""):
	local_data[area] = dict()
	if zone != "":
		local_data[area]["zone"] = zone
	if city != "":
		local_data[area]["city"] = city
	local_data[area]["region"] = region
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
def analyse_data(local_data, area_type):
	shifts = local_data["Shifts"]
	orders = local_data["Orders"]
	hours = local_data["Hours"]
	pay = local_data["Pay"]
	shifts_below_ten = local_data["Shifts < £10/h"]
	shifts_below_min = local_data["Shifts < min wage"]
	shifts_below_ten_percentage = round(shifts_below_ten / shifts, 4)
	shifts_below_min_percentage = round(shifts_below_min / shifts, 4)

	area = local_data[area_type]
	riders_data = get_data_for_area(area_type, area)
	riders = len(riders_data)
	if riders == 0:
		print(area, area_type)
		print(local_data)
		print(riders_data)
	riders_below_min = len([x for x in riders_data if x["< min"] == True])
	riders_below_min_percentage = round(riders_below_min / riders, 4)

	local_data["Hours"] = round(hours, 1)
	local_data["Riders"] = riders
	local_data["Orders per hour"] = round(orders / hours, 3)
	local_data["Shifts < £10/h (%)"] = shifts_below_ten_percentage
	local_data["Shifts < min wage (%)"] = shifts_below_min_percentage
	local_data["Hourly pay"] = round(pay / hours, 2)
	local_data["riders < min"] = riders_below_min
	local_data["riders < min (%)"] = riders_below_min_percentage

# Load riders yearly data
with open("data/tmp/riders-data-2.json", "r") as infile:
	riders_yearly_data = json.load(infile)
	riders_202021_data = get_data_for_financial_year(riders_yearly_data)

zones_data = dict()
cities_data = dict()
regions_data = dict()
# Loop though invoices to collect data by area and city
with open("data/tmp/iwgb-data-4.json", "r") as infile:
	iwgb_data = json.load(infile)
	current_fy = [x for x in iwgb_data if x["Financial year"] == "2020-21"]
	for invoice in current_fy:
		zone = invoice["zone"]
		city = invoice["city"]
		region = invoice["region"]

		# manual correction for one special case:
		if zone == "Oldham":
			zone = "Manchester"

		if zone not in zones_data:
			init_data(zones_data, zone, region, city, zone)
		increment_data(zones_data, zone, invoice)
		# Skip if no city could be matched to the area provided by the rider
		if city != "":
			if city not in cities_data:
				init_data(cities_data, city, region, city)
			increment_data(cities_data, city, invoice)
		# Skip if no city could be matched to the area provided by the rider
		if region != "":
			if region not in regions_data:
				init_data(regions_data, region, region)
			increment_data(regions_data, region, invoice)

# Analyse the data collected for each zone and city
for zone in zones_data:
	analyse_data(zones_data[zone], "zone")
for city in cities_data:
	analyse_data(cities_data[city], "city")
for region in regions_data:
	analyse_data(regions_data[region], "region")

# Remove the dictionaries keys and write the data to output files
print("[*] Writing the geo data to output files")
zones_data = [val for key, val in zones_data.items()]
cities_data = [val for key, val in cities_data.items()]
regions_data = [val for key, val in regions_data.items()]
write_csv_outfile(zones_data, "zones-data")
write_csv_outfile(cities_data, "cities-data")
write_csv_outfile(regions_data, "regions-data")

