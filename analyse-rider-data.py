import statistics
import datetime
import utils
import json

# TODO
# 1- refactor according to pep8

rider_years_data = dict()
with open("data/tmp/riders-data.json", "r") as infile:
	riders_yearly_data = json.load(infile)
	for rider_year in riders_yearly_data:
		# GENERAL ANALYSIS
		financial_year = rider_year["financial year"]
		city = rider_year["city"]
		hours = rider_year["hours"]
		pay = rider_year["pay"]
		basic_pay = rider_year["basic pay"]

		if hours != 0:
			hourly_pay = pay / hours
			hourly_basic_pay = basic_pay / hours
			minimum_wage = utils.yearly_minimum_wage[financial_year]
			pay_below_min = utils.is_pay_below_thres(hourly_pay, minimum_wage)
			rider_year["hourly pay"] = round(hourly_pay, 2)
			rider_year["hourly basic pay"] = round(hourly_basic_pay, 2)
			rider_year["< min"] = pay_below_min
		else:
			rider_year["hourly pay"] = "-"
			rider_year["hourly basic pay"] = "-"
			rider_year["< min"] = "-"

		# ANALYSIS OF WEEKLY DATA
		weeks = rider_year["weeks"]
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

		rider_year["Work weeks"] = len(weeks)
		if len(weeks) > 0:
			weekly_hours = [weeks[week]["hours"] for week in weeks]
			holiday = sum([weeks[week]["Holiday entitlement"] for week in weeks])
			holiday_pay = sum([weeks[week]["Holiday pay"] for week in weeks])
			pension = sum([weeks[week]["Pension contribution"] for week in weeks])
			with_no_benefits = (basic_pay - holiday_pay - pension) / hours

			rider_year["Median weekly hours"] = statistics.median(weekly_hours)
			rider_year["Holiday entitlement"] = holiday
			rider_year["Holiday pay"] = holiday_pay
			rider_year["Pension contribution"] = pension
			rider_year["Hourly basic pay without benefits"] = with_no_benefits
		else:
			rider_year["Median weekly hours"] = "-"
			rider_year["Holiday entitlement"] = "-"
			rider_year["Holiday pay"] = "-"
			rider_year["Pension contribution"] = "-"
			rider_year["Hourly basic pay without benefits"] = "-"
		
		# Remove the week by week data
		del rider_year["weeks"]

# remove keys and write output data to json file
with open('data/tmp/riders-data-2.json', 'w') as outfile:
    json.dump(riders_yearly_data, outfile)

# Remove dictionary keys and write the riders output data to csv file
print("[*] Writing the riders data to output file")
utils.write_csv_outfile(riders_yearly_data, "riders-data")
