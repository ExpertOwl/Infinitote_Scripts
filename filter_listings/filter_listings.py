# -*- coding: utf-8 -*-
"""
Created on Tuesday April 18, 2023

@author: Mark Zanon

Filters ebay listings based on specific criteria, used to generate sales. 


Instructions: Export csv file from stamps and put that file in the same directory as this script. Running the script will create a new csv file with a similar name as the stamps file. The name does not matter as long as it is a .csv file
If there are multiple .csv files, this script will try and filter sales for each.  
"""

import logging
import sys
import glob
import csv
import pandas as pd 
from re import search

#Can chose logging verbosity below:
# log_level = logging.DEBUG     #This will print a lot
log_level = logging.INFO        #This is just right 
# log_level = logging.WARNING   #This will print a little 
logging.basicConfig(format='%(levelname)s: %(message)s', level = log_level, force=True)


#Check if python version is compatable. This script relies on ordered dictionaries 
#Introduced in 3.7
if not sys.version_info >= (3, 7):
    logging.critical("filter_Listings.py requires python 3.7 or later, or orders will be scrambled")
    raise RuntimeError("filter_listings.py requires python 3.7 or later, or orders will be scrambled")