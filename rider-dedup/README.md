# riders-dedup

Where we find duplicated invoices with different rider ids, we need to collect the id pairs to replace the duplicate ids with the original ids

We do this to not overcount the number of riders in the data, which is especially important to be able to evaluate what our sample size is in different local area

It's also important in order to be able to make more accurate yearly calculation for riders for things like pay, hours per week, holiday entitlement and pension contribution

=================================================

## CODE

**Source:** `riders-dedup.py`

We spot duplicated invoices using a `long_string`, the string is made up of 4 of the 10 invoice datafields, including all `shifts` for which we use all five datafields available

For each invoice if no duplicate is found then we store the long string, but if we found a duplicate then we will store the pair of rider ids

The invoices are returned chronologically, in the order they were submitted by the API, we assign the first rider id we have seen as the original id and the one from the duplicated invoice as the duplicate id

Before storing the pair, we check if the id we've identified as the orgininal id, is already stored as the duplicate id of another pair

If it is than the original id of the latest pair needs to be re-assgined to match the original id of the pair we've already store, so we can flatten the pairs of duplicated ids from...

| Original id | Duplicate id |
| ----------- | ------------ |
| A           | B            |
| B           | C            |

to...

| Original id | Duplicate id |
| ----------- | ------------ |
| A           | B            |
| A           | C            |

The last thing we do before storing is to prioritise the actual Deliveroo rider id as the original id if it is available and we had identified it as the duplicate

There are two different formats of rider ids within the data, if the filename of the invoice PDFs submitted by the riders wasn't altered before being submit, then we can get the actual Deliveroo rider Id from the filename and that is the rider Id returned by the API, if not then we generate a custom rider id

The actual Deliveroo rider ids taken from the unaltered pdf filenames are longer than the generated ids so if the id we've identified as the duplicate id is longer than our identified original id we switch them over. In which case, we go through the pair of ids we've already stored to check if the shorter generated id was also identified as the original id of another pair, so that we can also re-assigned the original id of that pair for the actual Deliveroo rider id as well. So that...

| Original id | Duplicate id |
| ----------- | ------------ |
| A           | B            |
| A           | C            |

... where C is an actual Deliveroo rider id can be changed to...

| Original id | Duplicate id |
| ----------- | ------------ |
| C           | B            |
| C           | A            |

=================================================

## FUTURE CONSIDERATION

This only works to spot duplicates where we've been able to spot duplicated invoices in the data returned by IWGB's API

Now that that the invoice deduplication is running nightly to deal with duplicated invoices, it is unlikely that we will find much more duplicated rider ids, but that doesn't mean it isn't happening anymore

In all likely hood this will continue to happen at the same rate of around (10 %) as we've found them in the data when we first looked for them on 16/03/2021

Ideally the rider deduping should be handled at the same time as the invoice deduping process, but that will require more substancial thinkering around the logistics of the whole pdf parsing process 
