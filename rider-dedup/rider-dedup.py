import json
import csv

# write a long string made of the invoice data
# to find duplicated invoices with
# @param invoice: dict
def write_long_string(invoice):
	long_string = invoice["zone"] + invoice["start"] + invoice["end"]
	for shift in invoice["shifts"]:
		start = shift["start"]
		end = shift["end"]
		hours = str(shift["hours"])
		orders = str(shift["orders"])
		pay = str(shift["pay"])
		long_string += start + end + hours + orders + pay
	return long_string

# return a dictionary with the pair of rider ids
# @param original_id: string
# @param duplicate_id: string
def get_duplicate_data(original_id, duplicate_id):
	return {"Original Id": original_id, "Duplicate Id": duplicate_id}

# dict to store the duplicated invoices pairs of rider ids
# we use the duplicate id as the key, to be able to easily check
# if what we believe to be the original id is in fact the duplicate 
# of a pair ids we've already match, in which case the original id 
# of the new pair must be corrected to that of the pair we've already matched
duplicated_pairs = dict()

# for each invoice store a long string made of the invoice data as the key
# and the rider id as the val
seen = dict()
with open("iwgb-data-copy-for-dedup-20210318.json", "r") as infile:
	iwgb_data = json.load(infile)

	for invoice in iwgb_data:
		long_sting = write_long_string(invoice)

		# if we've already seen a duplicate of the invoice
		# we add the pair of rider ids to the duplicated pairs dict
		# otherwise we add the long string to the seen dict
		if long_string in seen:
			# invoices are returned by the API
			# in the order they were submitted
			# we initially set the first rider we have seen as the original
			# and the one from the duplicated invoice as the duplicate
			original_id = seen[long_string]
			duplicate_id = invoice["riderId"]
			# if they are the same id we can ignore the rest of the process
			if duplicate_id != original_id:
				# we go through stored pairs of duplicated invoices rider ids
				# and check if the id we think to be the original one is
				# the duplicate of a pair we've already matched
				# in which case the "original id" of the new pair
				# must be corrected to that of the pair we've already matched
				if original_id not in duplicated_pairs:
					# if the duplicate id is a longer id
					# taken from the invoice pdf file name
					# then we prioritise that as the original id
					if len(duplicate_id) > len(original_id):						
						duplicate_data = get_duplicate_data(duplicate_id, original_id)
						duplicated_pairs[duplicate_id] = duplicate_data
						# because we reverse a duplicate and an original id to
						# prioritise the id from file name we need to
						# go back and check if the orginal id
						# was also the original id of another pair
						# and switch the original id of that pair
						# to the longer id as well
						for rider_id in duplicated_pairs:
							if original_id == duplicated_pairs[rider_id]["Original Id"]:
								duplicated_pairs[rider_id]["Original Id"] = duplicate_id
					else:
						duplicate_data = get_duplicate_data(original_id, duplicate_id)
						duplicated_pairs[duplicate_id] = duplicate_data
				else:
					# change the original id
					# to that of the pair we've already match
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
