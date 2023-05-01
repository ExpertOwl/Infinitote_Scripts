# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 13:45:24 2022

@author: Mark Zanon

Converts stamps.com output to crossborderpickups manifest.


Instructions: Export csv file from stamps and put that file in the same directory as this script. Running the script will create a new csv file with a similar name as the stamps file. The name does not matter as long as it is a .csv file
If there are multiple .csv files, this script will try and create a manifest for each.  
"""

flag_value_over = 250

# TODO: Add logging function for trace debugging
# TODO: Put tracking number conversion into function with pd.apply() instead of inline with pd.any()
    
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
    logging.critical("StampsToManifest.py requires python 3.7 or later, or orders will be scrambled")
    raise RuntimeError("StampsToManifest.py requires python 3.7 or later, or orders will be scrambled")
    
#Define some Variables to make the code readable
#Cols to rename at end
rename_cols = {'Tracking #':'Tracking Number',
  'Recipient':'Recipient Full Name'}

states = {"AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California","CO":"Colorado","CT":"Connecticut","DE":"Delaware","FL":"Florida","GA":"Georgia","HI":"Hawaii","ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland","MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina","ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","PR":"Puerto Rico","RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia","WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming"}
#This list will be the final headers, in order. Don't leading delete spaces for item values. 
final_col_order = [
      'Order Number',
      'Recipient Full Name',
      'Business Name',
      'Address 1',
      'Address 2',
      'City',
      'State',
      'Zip Code',
      'Country',
      'Email',
      'Phone',
      'Reference Number',
      'Length',
      'Width',
      'Height',
      'Weight',
      'Lettermail?',
      'Tracking Number',
      'Carrier',
      'Item 1',
      'Item 1 Qty',
      ' Item 1 Value',
      'Item 1 Origin Country',
      'Item 2',
      'Item 2 Qty',
      ' Item 2 Value',
      'Item 2 Origin Country',
      'Item 3',
      'Item 3 Qty',
      ' Item 3 Value',
      'Item 3 Origin Country',
      ]



#list of cols to keep when imorting
keep_col = [
    'Recipient',
    'Tracking #',
    'Class Service',
    'Weight',
    'Printed Message',
    'Carrier'
    ]

recipient_headers = ['Recipient', 'Address 1', "City", "State", "Zip Code", "Country"] 
    
def check_headers(df):
    logging.debug(f'Checking headers for {file}')
    if list(df.keys()) == final_col_order:
        logging.info(f'skipping {file}')
        return(False)
    try:
        df = df[keep_col].copy()
    except:
        logging.debug(f'     Incorrect headers for {file}. If {file} is a stamps output, the headers may have changed. Adjust the names in keep_col above ' )
        logging.debug(f'     Skipping {file} \n')
        return(False)
    return(True)

def split_adress(order):
    order_adress = order["Recipient"].split(', ')
    logging.debug(f'\tParsing {order_adress}')
    #ebay adresses aren't standardized enough
    if not order["Recipient"].endswith('US'): 
        name, *adress, city, state_plus_zip = order_adress
        country = 'US'
    else:
        name, *adress, city, state_plus_zip, country = order_adress
         
    state, zip_code = state_plus_zip.split(' ')
    adress  = ' '.join(adress)
    return(name, adress, city , state, zip_code, country)
 
def get_value(order):
    item_code = order['Printed Message']
    code_is_nan = pd.isna(item_code)
    code_is_string = type(item_code) == str
    logging.debug(f'\tGetting value for {item_code}')
    if not code_is_string or code_is_nan:
        return(pd.NA)
    item_value = search(r'\d*$', item_code).group()
    if item_value == '':
        return(pd.NA) 
    return(float(item_value))
        
def remove_value(order):
    item_code = order['Printed Message']
    logging.debug(f'\tRemoving value for {item_code}')
    if pd.isna(item_code):
        return(item_code)
    else:
        item_value = order[' Item 1 Value']
        new_code = item_code.strip(str(item_value))
        return(new_code)

def print_warning(pdBool, error_type):
    orders_with_errors = [index+2 for index, has_error in enumerate(pdBool) if has_error]
    errors = {"high_value": 
                  f"The following lines have value >={flag_value_over}:\n{orders_with_errors}",
              "no_code":
                  f"The following lines have no printed code:\n{orders_with_errors}",
              'no_price':
                  f"Price not detecteed for the following lines:\n{orders_with_errors}",
              'no_state':f"Following lines do not have valid US states:{orders_with_errors}"}
    logging.warning(errors[error_type])


csv_files = glob.glob('*.csv')
for file in csv_files:
    logging.info(f"Working on {file}")
    file_name = file.split('.')[0]
    output_file = file_name + " Manifest.csv" 
    try:
        stamps_output = pd.read_csv(file, index_col=False) 
    except:
        logging.debug("couldn't parse {file}, headers may be wrong. Skipping...")
        continue
    #check that headers match expected stamps.com output 
    if not check_headers(stamps_output):
        continue
    ##Pull values from item codes
    stamps_output[' Item 1 Value'] = stamps_output.apply(get_value, axis = 1)
    stamps_output['Item 1'] = stamps_output.apply(remove_value, axis = 1)
    #Parse Adresses  
    new_addresses = stamps_output.apply(split_adress, axis = 1, result_type = 'expand')
    new_addresses.columns = recipient_headers
    stamps_output = stamps_output.drop(columns='Recipient')
    frames = [new_addresses, stamps_output]

    result = pd.concat(frames, axis=1)
    result['Weight'] = result['Weight'].str.split('lb', n=1,expand=True)[0].astype(int) +1
    
    #Rename some headers to CBP headers
    result = result.rename(rename_cols, axis = 1)
    result  = result.reindex(columns = final_col_order, fill_value = '')
    result['Lettermail?'] = 'N'
    result['Item 1 Qty'] = 1
    result['Item 1 Origin Country'] = 'US'   
    #Excel likes to format tracking numbers in scientific notion. There isn't 
    #anything I can do about it if the data is already bad when we read it in.
    #But forcing them to be strings will at least prevent program from crashing 
    result['Tracking Number'] = result['Tracking Number'].astype(str)
    if not result['Tracking Number'].str.contains('=').any():
        result['Tracking Number'] = '="'+result["Tracking Number"]+'"' 
        
    #Find misbehaving orders
    high_value = result[' Item 1 Value'] >= flag_value_over 
    no_code = result['Item 1'].isna()
    no_price = result[' Item 1 Value'].isna()
    no_state = ~result['State'].isin(states)
    
    errors = {'high_value':high_value, 'no_code':no_code, "no_price":no_price, "no_state":no_state}
    #cry wolf
    for error_type, orders_with_problems in errors.items():
        if orders_with_problems.any():
            print_warning(orders_with_problems, error_type)

    try:   
        result.to_csv(output_file, index=False, quoting=csv.QUOTE_MINIMAL)
    except PermissionError:
        logging.critical('Could not write to csv file. If the file open in excel, close it. Then open after running script \n')
        raise PermissionError('Could not write to csv file. If the file open in excel, close it. Then open after running script \n')

    logging.info(f'Done {file} -> {output_file} \n')        


