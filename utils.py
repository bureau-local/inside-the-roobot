import csv

# Minimum and living wage by year
yearly_minimum_wage = {
	"2020-21": 8.72,
	"2019-20": 8.21,
	"2018-19": 7.83,
	"2017-18": 7.50,
	"2016-17": 7.20
}

# Check if the val is below a certain treshreshold
# @params val: float
# @params threshold: float
def is_pay_below_thres(val, threshold):
	if val < threshold:
		return True
	else:
		return False

# write data to csv file
# @params output_data: list
# @params filename: string
def write_csv_outfile(output_data, filename):
	outfields = [datafield for datafield in output_data[0]]
	with open("data/out/" + filename + ".csv", "w") as outfile:
		writer = csv.DictWriter(outfile, fieldnames=outfields)
		writer.writeheader()
		writer.writerows(output_data)
