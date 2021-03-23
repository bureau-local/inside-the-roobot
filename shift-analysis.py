from utils import is_pay_below_thres, yearly_minimum_wage
import json

# Analysis - Get Pay/h, Pay<min wage and Orders/h for each
with open("data/tmp/iwgb-data-2.json", "r") as infile:
	iwgb_data = json.load(infile)
	# Go through each invoice
	for i, invoice in enumerate(iwgb_data):
		city = invoice["city"]
		shifts = invoice["shifts"]
		# Go through each shift
		for shift in shifts:
			pay = shift["Pay"]
			hours = shift["Hours"]
			orders = shift["Orders"]
			start = shift["Start"]

			# Get begining year of financial year i.e. 2020 for 2020-21
			year = int(start[:4])
			month = int(start[5:7])
			if month < 4:
				year += -1
			financial_year = str(year) + "-" + str((year + 1))[-2:]
			
			minimum_wage = yearly_minimum_wage[financial_year]
			hourly_pay = pay / hours

			shift["Hourly pay"] = hourly_pay
			shift["Pay < £10/h"] = is_pay_below_thres(hourly_pay, 10)
			shift["Pay < min"] = is_pay_below_thres(hourly_pay, minimum_wage)
			shift["Orders per hour"] = orders / hours
			shift["Financial year"] = financial_year

with open('data/tmp/iwgb-data-3.json', 'w') as outfile:
    json.dump(iwgb_data, outfile)