# inside-the-roobot
This is a repo for the Bureau’s investigation into Deliveroo's pay algorithm

=================================================

## CODE
STEP ONE - COLLECT EVERY INVOICE SUBMITTED TO IWGB

This is done with get-data-from-api.py

We collect everything except for invoices that weren't successfully parsed and test data. We include the date in the output file's name in case we need to refer to an earlier version of the data at some point in the future.

step two - dedup-rider-ids.py

step three - geo-cleaning.py

step four - shift-analysis.py

step five - invoice-analysis.py


Then the various parse scripts produce the output files
