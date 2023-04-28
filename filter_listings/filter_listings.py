# -*- coding: utf-8 -*-
"""
Created on Tuesday April 18, 2023

@author: Mark Zanon

Filters ebay listings based on specific criteria, used to generate sales. 


Instructions: Export csv file from ebay and put that file in the same directory as this script.

Set the variables to filter out the listings you want:
    
get_listings_in_date_range -> If true, wull pull skus before get_before and after get_after:
    i.e. get_after  <= SKU <= get_before 
    get_after 2200 and get_before 2300 will pull everything between 2200 and 2300

get_invalid_date_codes -> if = True, gets all skus codes that do not have a date code. Specifically checks for four consecutive numbers
get_u -> if = True, get date codes that start with U-
get_n -> if = True, get date codes that start with N-

exclude_games -> If true, ignore all date codes that have include "GAME"

    
"""

# import csv
import glob
import logging
import re
import functools
import pandas as pd 

# make script ignore csv files correctly. 
get_before = 2252
get_after = 2240
get_invalid_date_codes = True
get_u = True
get_n = True
get_listings_in_date_range = True
#Games date codes are a mess right now, exclude_games = true excludes games from the filter. 
exclude_games = True

#Can chose logging verbosity below:
log_level = logging.INFO        #This is just right 
logging.basicConfig(format='%(levelname)s: %(message)s', level = log_level, force=True)

csv_files = glob.glob('*.csv')
for file in csv_files:
    logging.debug(f"{file}")
    filename = file.split('.')[0]
    if filename.endswith('filtered'):
        logging.info(f"File name ends with _filtered, skipped")
        continue
    logging.info(f"Working on {file}")
    append_to_filename = [] 
    ors = []
    ands = []
    all_listings = pd.read_csv(file)

    skus = all_listings['Custom label (SKU)']
    datecodes = skus.str.extract("(\d{4})")[0]
    datecodes_as_int = datecodes.fillna(0).astype(int)
    #Build masks here
    #masks to be OR-d
    starts_with_u = skus.str.contains("^U-")
    starts_with_n = skus.str.contains("^N-")
    is_in_date_range = (datecodes_as_int < get_before) & (datecodes_as_int >= get_after) 
    is_valid = datecodes_as_int != 0 

    if get_listings_in_date_range:
        ors.append(is_in_date_range)
        append_to_filename.append(f"{get_after}-{get_before}")
    if get_u:
        ors.append(starts_with_u)
        append_to_filename.append("+U")
    if get_n:
        ors.append(starts_with_n)
        append_to_filename.append("+N")
    if get_invalid_date_codes:
        ors.append(~is_valid)
        append_to_filename.append("+invalid")
        
    #masks to be And-ed
    is_not_game = ~skus.str.contains(re.compile(".*GAME.*"))
    
    if exclude_games: 
        ands.append(is_not_game)
        append_to_filename.append("+NOGAMES")
    
    if ors:
        #OR all masks that should be OR'd 
        export = functools.reduce(lambda x,y: x | y, ors)
    if ands: 
        #AND result with all other masks that should be AND'd
        export = export & functools.reduce(lambda x,y: x & y, ands)
    
    #failsafe for if 0 listings were exported. Prevents ValueError
    if not True in export.value_counts():
        num_exports = 0 
    else: 
        num_exports = export.value_counts()[True]
    logging.info(f"Filtered {num_exports} out of {len(all_listings)} listings")
    #build final df
    #Generate export filename based on settigs
    append_to_filename = '_'.join(append_to_filename)
    outfile = f'{filename}_{append_to_filename}_filtered.csv'
    #Filter all listing swith final mask 
    rows_with_matching_skus = all_listings[export]
    rows_with_matching_skus.to_csv(f'{outfile}', index=False)
    logging.info(f"Exported to {outfile}")