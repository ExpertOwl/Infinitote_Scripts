# -*- coding: utf-8 -*-
"""
Created on Tuesday April 18, 2023

@author: Mark Zanon

Filters ebay listings based on specific criteria, used to generate sales. 


Instructions: Export csv file from ebay and put that file in the same directory as this script.
Running the script will create a new csv and will pull out all rows with skus matching this criteria:

    
"""

# import csv
import glob
import logging
import re
import functools
import pandas as pd 

# make script ignore csv files correctly. 

pull_before = 2252
pull_after = 2240
pull_invalid_date_codes = False
pull_u = False
pull_n = False
pull_listings_in_date_range = True
exclude_games = True

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
    ors = []
    ands = []
    all_listings = pd.read_csv(file)

    outfile = f'{filename}_filtered.csv'
    skus = all_listings['Custom label (SKU)']
    datecodes = skus.str.extract("(\d{4})")[0]
    datecodes_as_int = datecodes.fillna(0).astype(int)
    #Build masks here
    #masks to be OR-d
    starts_with_u = skus.str.contains("^U-")
    starts_with_n = skus.str.contains("^N-")
    is_in_date_range = (datecodes_as_int < pull_before) & (datecodes_as_int >= pull_after) 
    is_valid = datecodes_as_int != 0 
    
    if pull_u:
        ors.append(starts_with_u)
    if pull_n:
        ors.append(starts_with_n)
    if pull_listings_in_date_range:
        ors.append(is_in_date_range)
    if pull_invalid_date_codes:
        ors.append(~is_valid)
        
    #masks to be And-ed
    is_not_game = ~skus.str.contains(re.compile(".*GAME.*"))
    
    if exclude_games: 
        ands.append(is_not_game)
    
    #Bool ors
    if ors:
        export = functools.reduce(lambda x,y: x | y, ors)
    if ands: #Bool result with ands list
        export = export & functools.reduce(lambda x,y: x & y, ands)
        
    if not True in export.value_counts():
        num_exports = 0 
    else: 
        num_exports = export.value_counts()[True]
    logging.info(f"Filtered {num_exports} out of {len(all_listings)} listings")
    #build final df
    rows_with_matching_skus = all_listings[export]
    
    rows_with_matching_skus.to_csv(f'{outfile}', index=False)
    logging.info(f"Exported to {outfile}")