from utils import is_pay_below_thres, yearly_minimum_wage
import json

# Analysis
with open("data/tmp/iwgb-data-3.json", "r") as infile:
	iwgb_data = json.load(infile)
	# Go through each invoice
	for i, invoice in enumerate(iwgb_data):
		# if i > 100:
			# break
		invoice_id = invoice["id"]
		city = invoice["city"]
		shifts = invoice["shifts"]
		adjustments = invoice["adjustments"]

		drop_fees = sum([shift["Pay"] for shift in shifts])
		
		# We don't count transaction fees or tips in the total adjustment figure
		adjustments_total = 0
		for adjustment in adjustments:
			if adjustment["Label"] not in ["Transaction fee", "Tips"]:
				adjustments_total += adjustment["Amount"]

		total_pay = drop_fees + adjustments_total
		hours = sum([shift["Hours"] for shift in shifts])
		orders = sum([shift["Orders"] for shift in shifts])

		# Get begining year of financial year i.e. 2020 for 2020-21
		start = invoice["start"]
		year = int(start[:4])
		month = int(start[5:7])
		if month < 4:
			year += -1
		financial_year = str(year) + "-" + str((year + 1))[-2:]

		if hours != 0:
			minimum_wage = yearly_minimum_wage[financial_year]
			hourly_pay = total_pay / hours
			pay_below_min = is_pay_below_thres(hourly_pay, minimum_wage)
			basic_pay = drop_fees / hours
			basic_pay_below_min = is_pay_below_thres(basic_pay, minimum_wage)
		else:
			hourly_pay = "-"
			pay_below_min = "-"
			basic_pay = "-"
			basic_pay_below_min = "-"

		shifts_count = len(shifts)
		count_below_ten = len([x for x in shifts if x["Pay < £10/h"] == True])
		count_below_min = len([x for x in shifts if x["Pay < min"] == True])

		invoice["Financial year"] = financial_year
		invoice["Drop Fees"] = round(drop_fees, 2)
		invoice["Total Pay"] = round(total_pay, 2)
		invoice["Hours"] = hours
		invoice["Hourly pay"] = hourly_pay
		invoice["Pay < min wage"] = pay_below_min
		invoice["Basic pay"] = basic_pay
		invoice["Basic pay < min wage"] = basic_pay_below_min
		invoice["Number of shifts"] = shifts_count
		invoice["Shifts < £10/h"] = count_below_ten
		invoice["Shifts < min wage"] = count_below_min
		invoice["Total orders"] = orders

with open('data/tmp/iwgb-data-4.json', 'w') as outfile:
    json.dump(iwgb_data, outfile)
