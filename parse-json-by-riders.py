import statistics
import datetime
import json
import csv

# TODO
# 1- make script shorter... perhaps by spliting in two... or three, first a json with week data then the weekly data analysis than the parsing

# Minimum and living wage by year
yearly_minimum_wage = {
	"2020-21": 8.72,
	"2019-20": 8.21,
	"2018-19": 7.83,
	"2017-18": 7.50,
	"2016-17": 7.20
}

# Check if pay is below threshold
def is_pay_below_thres(val, threshold):
	if val < threshold:
		return True
	else:
		return False

date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
rider_years_data = dict()
# Analysis
with open("data/tmp/iwgb-data-4.json", "r") as infile:
	iwgb_data = json.load(infile)
	for i, invoice in enumerate(iwgb_data):
		# if i > 10:
			# break
		rider_id = invoice["riderId"]
		start = invoice["start"]
		
		# Get the financial year based on the invoice start date
		year = int(start[:4])
		month = int(start[5:7])
		if month < 4:
			year += -1
		financial_year = str(year) + "-" + str((year + 1))[-2:]

		rider_year = rider_id + "_" + financial_year
		if rider_year not in rider_years_data:
			rider_years_data[rider_year] = dict()
			rider_years_data[rider_year]["Rider Id"] = rider_id
			rider_years_data[rider_year]["vehicle"] = invoice["vehicle"]
			rider_years_data[rider_year]["zone"] = invoice["zone"]
			rider_years_data[rider_year]["city"] = invoice["city"]
			rider_years_data[rider_year]["financial year"] = financial_year
			rider_years_data[rider_year]["invoices"] = 0
			rider_years_data[rider_year]["shifts"] = 0
			rider_years_data[rider_year]["orders"] = 0
			rider_years_data[rider_year]["hours"] = 0
			rider_years_data[rider_year]["pay"] = 0
			rider_years_data[rider_year]["basic pay"] = 0
			rider_years_data[rider_year]["weeks"] = dict()

		for shift in invoice["shifts"]:
			# print(shift)
			start = shift["Start"]
			start_date = datetime.datetime.strptime(start, date_format)
			week = start_date.strftime("%V")
			if week not in rider_years_data[rider_year]["weeks"]:
				init_data = dict()
				init_data["hours"] = 0
				init_data["pay"] = 0
				rider_years_data[rider_year]["weeks"][week] = init_data

			weekly_data = rider_years_data[rider_year]["weeks"][week]
			weekly_data["hours"] += shift["Hours"]
			weekly_data["pay"] += shift["Pay"]
			rider_years_data[rider_year]["weeks"][week] = weekly_data
			# break

		rider_years_data[rider_year]["invoices"] += 1
		rider_years_data[rider_year]["shifts"] += invoice["Number of shifts"]
		rider_years_data[rider_year]["orders"] += invoice["Total orders"]
		rider_years_data[rider_year]["hours"] += invoice["Hours"]
		rider_years_data[rider_year]["pay"] += invoice["Total Pay"]
		rider_years_data[rider_year]["basic pay"] += invoice["Drop Fees"]

# GENERAL ANALYSIS
for rider_year in rider_years_data:
	rider_data = rider_years_data[rider_year]
	financial_year = rider_data["financial year"]
	city = rider_data["city"]
	hours = rider_data["hours"]
	pay = rider_data["pay"]
	basic_pay = rider_data["basic pay"]
	weeks = rider_data["weeks"]

	if hours != 0:
		hourly_pay = pay / hours
		hourly_basic_pay = basic_pay / hours
		minimum_wage = yearly_minimum_wage[financial_year]
		pay_below_min = is_pay_below_thres(hourly_pay, minimum_wage)
		rider_data["hourly pay"] = round(hourly_pay, 2)
		rider_data["hourly basic pay"] = round(hourly_basic_pay, 2)
		rider_data["< min"] = pay_below_min
	else:
		rider_data["hourly pay"] = "-"
		rider_data["hourly basic pay"] = "-"
		rider_data["< min"] = "-"

	# ANALYSIS OF WEEKLY DATA
	for week in weeks:
		holiday_entitlement = weeks[week]["hours"] / 52 * 5.6
		if holiday_entitlement > 4.31:
			holiday_entitlement = 4.31

		hourly_pay = weeks[week]["pay"] / weeks[week]["hours"]
		holiday_pay = holiday_entitlement * hourly_pay

		if weeks[week]["pay"] > 120:
			pension_contribution = weeks[week]["pay"] / 100 * 3
		else:
			pension_contribution = 0

		weeks[week]["Holiday entitlement"] = holiday_entitlement
		weeks[week]["Holiday pay"] = holiday_pay
		weeks[week]["Pension contribution"] = pension_contribution

	rider_data["Work weeks"] = len(weeks)
	if len(weeks) > 0:
		weekly_hours = [weeks[week]["hours"] for week in weeks]
		holiday = sum([weeks[week]["Holiday entitlement"] for week in weeks])
		holiday_pay = sum([weeks[week]["Holiday pay"] for week in weeks])
		pension = sum([weeks[week]["Pension contribution"] for week in weeks])
		with_no_benefits = (basic_pay - holiday_pay - pension) / hours

		rider_data["Median weekly hours"] = statistics.median(weekly_hours)
		rider_data["Holiday entitlement"] = holiday
		rider_data["Holiday pay"] = holiday_pay
		rider_data["Pension contribution"] = pension
		rider_data["Hourly basic pay without benefits"] = with_no_benefits
	else:
		rider_data["Median weekly hours"] = "-"
		rider_data["Holiday entitlement"] = "-"
		rider_data["Holiday pay"] = "-"
		rider_data["Pension contribution"] = "-"
		rider_data["Hourly basic pay without benefits"] = "-"
	
	# Remove the week by week data
	del rider_data["weeks"]
	rider_years_data[rider_year] = rider_data

# Write the cities data to output file
print("[*] Writing the riders data to output file")
rider_years_data = [val for key, val in rider_years_data.items()]
outfields = [datafield for datafield in rider_years_data[0]]
with open("data/out/riders-data.csv", "w") as outfile:
	writer = csv.DictWriter(outfile, fieldnames=outfields)
	writer.writeheader()
	writer.writerows(rider_years_data)
