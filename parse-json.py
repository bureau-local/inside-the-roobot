from utils import write_csv_outfile
import json

def init_data(data_dict, invoice):
	data_dict["Invoice id"] = invoice["id"]
	data_dict["Rider id"] = invoice["riderId"]
	data_dict["Vehicle"] = invoice["vehicle"]
	data_dict["Zone"] = invoice["zone"]
	data_dict["City"] = invoice["city"]
	data_dict["Region"] = invoice["region"]
	return data_dict

invoices = list()
shifts = list()
# Parse the json 
with open("data/tmp/iwgb-data-4.json", "r") as infile:
	iwgb_data = json.load(infile)
	for i, invoice in enumerate(iwgb_data):
		# Parse the invoice data
		invoice_data = init_data(dict(), invoice)
		invoice_data["Financial year"] = invoice["Financial year"]
		invoice_data["Start date"] = invoice["start"]
		invoice_data["End date"] = invoice["end"]
		invoice_data["Drop Fees"] = invoice["Drop Fees"]

		tips = 0
		adjustments = 0
		transaction_fee = 0
		other_adjustments = 0
		for adjustment in invoice["adjustments"]:
			if adjustment["Label"] == "Tips":
				tips += adjustment["Amount"]
			elif adjustment["Label"] == "Adjustments":
				adjustments += adjustment["Amount"]
			elif adjustment["Label"] == "Transaction Fee":
				adjustments += adjustment["Transaction Fee"]
			else:
				other_adjustments += adjustment["Amount"]

		invoice_data["Tips"] = tips
		invoice_data["Adjustments"] = adjustments
		invoice_data["Transaction fee"] = transaction_fee
		invoice_data["Other adjustments"] = other_adjustments
		invoice_data["Total Pay"] = invoice["Total Pay"]
		invoice_data["Hours"] = invoice["Hours"]
		invoice_data["Hourly pay"] = invoice["Hourly pay"]
		invoice_data["Pay < min wage"] = invoice["Pay < min wage"]
		invoice_data["Basic pay"] = invoice["Basic pay"]
		invoice_data["Basic pay < min wage"] = invoice["Basic pay < min wage"]
		invoice_data["Number of shifts"] = invoice["Number of shifts"]
		invoice_data["Shifts < min wage"] = invoice["Shifts < min wage"]
		invoice_data["Total orders"] = invoice["Total orders"]
		invoices.append(invoice_data)

		# Parse the shifts data
		for shift in invoice["shifts"]:
			shift_data = init_data(dict(), invoice)
			shift_data.update(shift)
			shifts.append(shift_data)

# Write the invoice and shifts data to output file
print("[*] Writing the invoices and shifts data to output file")
write_csv_outfile(invoices, "invoices")
write_csv_outfile(shifts, "shifts")

