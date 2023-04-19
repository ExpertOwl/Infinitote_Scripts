# -*- coding: utf-8 -*-
"""
Created on Tuesday April 18, 2023

@author: Mark Zanon

Filters ebay listings based on specific criteria, used to generate sales. 


Instructions: Export csv file from ebay and put that file in the same directory as this script.
Running the script will create a new csv and will pull out all rows with skus matching this criteria:
    sku does not contain GAME
    AND...
    Starts with U- 
    OR
    Starts with N- 
    OR
    Date code < pull_before (set below)
    OR
    No/invalid date code
    can add or remove masks to the ors list or ands list to change what is pulled
    
"""

# import csv
import glob
import logging
import re
import functools
import pandas as pd 


pull_before = 2240

#Can chose logging verbosity below:
log_level = logging.INFO        #This is just right 
logging.basicConfig(format='%(levelname)s: %(message)s', level = log_level, force=True)


csv_files = glob.glob('*.csv')
for file in csv_files:
    logging.info(f"Working on {file}")
    filename = file.split('.')[0]
    if filename.endswith('filtered'):
        logging.info(f"{file} ends with _filtered. Skipping {file}")
        continue
    all_listings = pd.read_csv(file)

    outfile = f'{filename}_filtered.csv'
    skus = all_listings['Custom label (SKU)']
    datecodes = skus.str.extract("(\d{4})")[0]
    datecodes_as_int = datecodes.fillna(0).astype(int)
    #Build masks here
    #masks to be OR-d
    starts_with_u = skus.str.contains("^U-")
    starts_with_n = skus.str.contains("^N-")
    is_old_or_invalid = datecodes_as_int < pull_before
    ors = [starts_with_u,
           starts_with_n,
           is_old_or_invalid,
           ]
    #masks to be And-ed
    is_not_game = ~skus.str.contains(re.compile(".*GAME.*"))
    ands = [is_not_game,
            ]
    
    #Bool ors
    export = functools.reduce(lambda x,y: x | y, ors)
    #Bool result with ands list
    export = export & functools.reduce(lambda x,y: x & y, ands)
    
    logging.info(f"Filtered {export.value_counts()[True]} out of {len(all_listings)} listings")
    #build final df
    rows_with_matching_skus = all_listings[export]
    
    rows_with_matching_skus.to_csv(f'{outfile}', index=False)
    logging.info(f"Exported to {outfile}")