import json
import csv

# write a long string made of the invoice data to spot duplicated invoices
# @param invoice: dict
def write_long_string(invoice):
	long_string = invoice["zone"] + invoice["start"] + invoice["end"]
	for shift in invoice["shifts"]:
		start = shift["Start"]
		end = shift["End"]
		hours = str(shift["Hours"])
		orders = str(shift["Orders"])
		pay = str(shift["Pay"])
		long_string += start + end + hours + orders + pay
	return long_string

# return a dictionary with the pair of rider ids
# @param original_id: string
# @param duplicate_id: string
def get_duplicate_data(original_id, duplicate_id):
	return {"Original Id": original_id, "Duplicate Id": duplicate_id}

# Store the duplicated invoices pair of rider ids in a dict
# with the duplicate id as the key, so we can check if the orgininal id
# of a new pair, is already stored as the duplicate id of another pair
duplicated_pairs = dict()

# Store the rider id, with a long string made of the invoice data as the key
seen = dict()
# filename = "data_with_dupes.json"
filename = "iwgb-data-copy-for-dedup-20210318.json"
with open(filename, "r") as infile:
	iwgb_data = json.load(infile)

	for invoice in iwgb_data:
		long_string = write_long_string(invoice)

		# store the pair of rider ids if we've already seen
		# a duplicate of the invoice or store the long string if we haven't
		if long_string in seen:
			# we initially set the first rider id we have seen as the original
			# and the one from the duplicated invoice as the duplicate
			original_id = seen[long_string]
			duplicate_id = invoice["riderId"]
			# if they are the same id we can ignore the rest of the process
			if duplicate_id != original_id:
				# Check if the "original id" has already been stored as
				# the duplicate of another pair in which case it is
				# re-assigned to match the original id of that pair
				if original_id not in duplicated_pairs:
					# check if the duplicate id is the actual (longer)
					# deliveroo id and prioritise it as the original id
					if len(duplicate_id) > len(original_id):						
						duplicate_data = get_duplicate_data(duplicate_id, original_id)
						duplicated_pairs[duplicate_id] = duplicate_data
						# check if the original id had already been stored as
						# the original id of another pair, and re-assign the
						# original id of that pair to the actual deliveroo id
						for rider_id in duplicated_pairs:
							if original_id == duplicated_pairs[rider_id]["Original Id"]:
								duplicated_pairs[rider_id]["Original Id"] = duplicate_id
					else:
						duplicate_data = get_duplicate_data(original_id, duplicate_id)
						duplicated_pairs[duplicate_id] = duplicate_data
				else:
					# update the original id before storing the pair
					original_id = duplicated_pairs[original_id]["Original Id"]
					duplicate_data = get_duplicate_data(original_id, duplicate_id)
					duplicated_pairs[duplicate_id] = duplicate_data
		else:
			seen[long_string] = invoice["riderId"]

# Write the duplicated pair of ids to output file
outfields = ["Original Id", "Duplicate Id"]
duplicated_pairs = [val for key, val in duplicated_pairs.items()]
with open("duplicated-pairs.csv", "w") as outfile:
	writer = csv.DictWriter(outfile, fieldnames=outfields)
	writer.writeheader()
	writer.writerows(duplicated_pairs)
