from utils import get_financial_year
import datetime
import json

# increment the riders yearly data when looping through each invoices
# @params rider_data: dict
# @params invoice: dict
def increment_riders_data(rider_data, invoice):
	rider_data["invoices"] += 1
	rider_data["shifts"] += invoice["Number of shifts"]
	rider_data["orders"] += invoice["Total orders"]
	rider_data["hours"] += invoice["Hours"]
	rider_data["pay"] += invoice["Total Pay"]
	rider_data["basic pay"] += invoice["Drop Fees"]

date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
riders_yearly_data = dict()
# Analysis
with open("data/tmp/iwgb-data-4.json", "r") as infile:
	iwgb_data = json.load(infile)
	for invoice in iwgb_data:
		rider_id = invoice["riderId"]
		# Get the financial year based on the invoice start date
		start = invoice["start"]
		financial_year = get_financial_year(start)
		
		rider_year = rider_id + "_" + financial_year
		if rider_year not in riders_yearly_data:
			riders_yearly_data[rider_year] = dict()
			riders_yearly_data[rider_year]["Rider Id"] = rider_id
			riders_yearly_data[rider_year]["vehicle"] = invoice["vehicle"]
			riders_yearly_data[rider_year]["zone"] = invoice["zone"]
			riders_yearly_data[rider_year]["city"] = invoice["city"]
			riders_yearly_data[rider_year]["region"] = invoice["region"]
			riders_yearly_data[rider_year]["financial year"] = financial_year
			riders_yearly_data[rider_year]["invoices"] = 0
			riders_yearly_data[rider_year]["shifts"] = 0
			riders_yearly_data[rider_year]["orders"] = 0
			riders_yearly_data[rider_year]["hours"] = 0
			riders_yearly_data[rider_year]["pay"] = 0
			riders_yearly_data[rider_year]["basic pay"] = 0
			riders_yearly_data[rider_year]["weeks"] = dict()

		for shift in invoice["shifts"]:
			start = shift["Start"]
			start_date = datetime.datetime.strptime(start, date_format)
			week = start_date.strftime("%V")
			if week not in riders_yearly_data[rider_year]["weeks"]:
				init_data = dict()
				init_data["hours"] = 0
				init_data["pay"] = 0
				riders_yearly_data[rider_year]["weeks"][week] = init_data

			weekly_data = riders_yearly_data[rider_year]["weeks"][week]
			weekly_data["hours"] += shift["Hours"]
			weekly_data["pay"] += shift["Pay"]
			riders_yearly_data[rider_year]["weeks"][week] = weekly_data

		increment_riders_data(riders_yearly_data[rider_year], invoice)

# remove keys and write output data to json file
riders_yearly_data = [val for key, val in riders_yearly_data.items()]
with open('data/tmp/riders-data.json', 'w') as outfile:
    json.dump(riders_yearly_data, outfile)
