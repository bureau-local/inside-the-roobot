from utils import write_csv_outfile
import statistics
import datetime
import json

# we are matching by invoice as we wouldn't be able to use the adjustment data otherwise
# we match the financial year using the start date, as the financial year goes up every year
# we are giving them some leeway and not penalising them by doing so
# and the error on your side is likely minimal

def get_data_for_financial_year(riders_yearly_data, year):
	return [x for x in riders_yearly_data if x["financial year"] == year]

# Load riders yearly data
with open("data/tmp/riders-data-2.json", "r") as infile:
	riders_yearly_data = json.load(infile)

yearly_data = dict()
# Go through each invoice and shift
with open("data/tmp/iwgb-data-4.json", "r") as infile:
	iwgb_data = json.load(infile)

	for i, invoice in enumerate(iwgb_data):
		rider_id = invoice["riderId"]
		start = invoice["start"]
		shifts_below_ten = invoice["Shifts < £10/h"]
		shifts_below_min = invoice["Shifts < min wage"]

		# Get the financial year based on the shift start date
		year = int(start[:4])
		month = int(start[5:7])
		if month < 4:
			year += -1
		financial_year = str(year) + "-" + str((year + 1))[-2:]

		if financial_year not in yearly_data:
			yearly_data[financial_year] = dict()
			yearly_data[financial_year]["financial year"] = financial_year
			yearly_data[financial_year]["shifts"] = 0
			yearly_data[financial_year]["orders"] = 0
			yearly_data[financial_year]["hours"] = 0
			yearly_data[financial_year]["pay"] = 0
			yearly_data[financial_year]["basic pay"] = 0
			yearly_data[financial_year]["shifts < ten"] = 0
			yearly_data[financial_year]["shifts < min"] = 0

		yearly_data[financial_year]["shifts"] += invoice["Number of shifts"]
		yearly_data[financial_year]["orders"] += invoice["Total orders"]
		yearly_data[financial_year]["hours"] += invoice["Hours"]
		yearly_data[financial_year]["pay"] += invoice["Total Pay"]
		yearly_data[financial_year]["basic pay"] += invoice["Drop Fees"]
		yearly_data[financial_year]["shifts < ten"] += shifts_below_ten
		yearly_data[financial_year]["shifts < min"] += shifts_below_min

# Analyse the data collected by year
for year in yearly_data:
	shifts = yearly_data[year]["shifts"]
	shifts_below_ten = yearly_data[year]["shifts < ten"] 
	shifts_below_min = yearly_data[year]["shifts < min"] 
	orders = yearly_data[year]["orders"]
	hours = yearly_data[year]["hours"]
	pay = yearly_data[year]["pay"]
	basic_pay = yearly_data[year]["basic pay"]

	riders_data = get_data_for_financial_year(riders_yearly_data, year)
	riders = len(riders_data)
	riders_below_min = len([x for x in riders_data if x["< min"] == True])
	riders_below_min_percentage = round(riders_below_min / riders, 4)

	if hours != 0:
		hourly_pay = round(pay / hours, 2)
		hourly_basic_pay = round(basic_pay / hours, 2)
		orders_per_hour = round(orders / hours, 3)
	else:
		hourly_pay = "-"
		hourly_basic_pay = "-"
		orders_per_hour = "-"

	if shifts != 0:
		shifts_below_ten_percentage = round(shifts_below_ten / shifts, 4)
		shifts_below_min_percentage = round(shifts_below_min / shifts, 4)
	else:
		shifts_below_ten_percentage = "-"
		shifts_below_min_percentage = "-"

	yearly_data[year]["hours"] = round(hours, 1)
	yearly_data[year]["riders"] = riders
	yearly_data[year]["pay"] = round(pay, 2)
	yearly_data[year]["basic pay"] = round(basic_pay, 2)
	yearly_data[year]["hourly pay"] = hourly_pay
	yearly_data[year]["hourly basic pay"] = hourly_basic_pay
	yearly_data[year]["orders per hour"] = orders_per_hour
	yearly_data[year]["shifts < ten (%)"] = shifts_below_ten_percentage
	yearly_data[year]["shifts < min (%)"] = shifts_below_min_percentage
	yearly_data[year]["riders < min"] = riders_below_min
	yearly_data[year]["riders < min (%)"] = riders_below_min_percentage

# Remove the dictionary keys and write the yearly data to output file
print("[*] Writing the yearly data to output file")
yearly_data = [val for key, val in yearly_data.items()]
write_csv_outfile(yearly_data, "yearly-breakdown")
