# inside-the-roobot
This is a repo for the Bureau’s investigation into Deliveroo's pay algorithm

=================================================

## CODE

#### STEP ONE - COLLECT EVERY INVOICES SUBMITTED TO IWGB

**Source:** `get-data-from-api.py`

We collect everything except for invoices that weren't successfully parsed and test data. We include the date in the output file's name in case we need to refer to an earlier version of the data at some point in the future

---

#### STEP TWO - REMOVE DUPLICATED RIDER IDS

**Source:** `dedup-rider-ids.py`

Where we've found duplicated invoices with different rider ids, we collected the id pairs (see the riders-dedup folder for this) and we now replace the duplicate ids with the original ids

We do this to not overcount the number of riders in the data, which is especially important to be able to evaluate what our sample size is in different local area

It's also important in order to be able to make more accurate yearly calculation for riders for things like pay, hours per week, holiday entitlement and pension contribution

---

#### STEP THREE - MATCH THE RIDER SUBMITTED ZONE TO THE CITY 

**Source:** `geo-cleaning.py`

The `zone` datafield returned by the api is not derived from the invoice but is enterred by the rider in a free text field when they submit their invoices. This leads to a number of issues, with some riders inputting the actual deliveroo working zone code, other inputting the name of a city or neighbourhood and obviously with the occasional spelling mistake as well

This is where we clean all of that, matching everything up to city level. We use two lookup files to help us with that, `zone-city-lookup.csv` and `area-city-lookup.csv`

`zone-city-lookup.csv` helps with matching Deliveroo working zones to cities. It mainly comes from the deliveroo incentives webpage but was complemented by the occasional search from within the rider app by partnering riders

`area-city-lookup.csv` helps with matching all other free text entries to cities. It was built manually as the different areas entered by riders trickled in

There are a few entries that unfortunately couldn't be matched to a city, because they were too imprecise ("City center"), too large ("South"), or when the rider mistakenly entered the vehicle type instead (which is another field that relies on user input)

---

#### STEP FOUR - ANALYSE DATA FROM EACH SHIFT

**Source:** `shift-analysis.py`

We analyse the data from each shift to get the financial year, the hourly pay, whether the shift paid below £10 per hour or not, whether the shift paid the rider below the equivalent of the [minimum wage](https://www.gov.uk/national-minimum-wage-rates) or not and the number of orders per hour

---

#### STEP FIVE - ANALYSE DATA FROM EACH INVOICE

**Source:** `invoice-analysis.py`

We analyse the data from each invoice to get the drop fees, the total pay, the hours worked, the hourly pay, the basic pay, whether the hourly pay was below the [minimum wage](https://www.gov.uk/national-minimum-wage-rates) or not, whether the basic pay was below the minimum wage or not, the number of shifts, the number of shifts that paid below £10 per hour, the number of shifts that paid below the minimum wage and the total number of orders delivered

The total pay includes drop fees and adjustments except tips and transaction fees (from when the rider requests their invoices before the end of the pay period)

The basic pay only includes drop fees, with all adjustments excluded from the total

---

#### WRITING THE OUTPUT FILES

**Source:** `parse-json.py`, `parse-by-year.py`, `parse-json-by-riders.py`, `parse-by-area.py` 

We use four different scripts to prepare a number of different output files to allow us to look at the data a number of different ways, either by looking directly at the shifts and invoices, at yearly breakdown, at each individual riders or at each city

Holiday entitlement and pension contribution calculations as well as the average number of hours worked per week for each rider are made within `parse-json-by-riders.py`

---
