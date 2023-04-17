# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 13:45:24 2022

@author: Mark Zanon

Converts stamps.com output to crossborder manifest.


Instructions: Export csv file from stamps and put that file in the same directory as this script. Running the script will create a new csv file with a similar name as the stamps file. The name does not matter as long as it is a .csv file
If there are multiple .csv files, this script will try and create a manifest for each.  
"""
verbose = False

#imports
import pandas as pd 
import sys
import glob
import math
from collections import defaultdict
from re import search


#Check if python version is compatable. This script relies on ordered dictionaries 
#Introduced in 3.7
if not sys.version_info >= (3, 7):
    print("""This script requires python version > 3.7 or the dictionary operations
          will be out of order, and the adresses will not match corresponding order numbers""")
    sys.exit()
    
#Define some Variables to make the code read nicer 
#Cols to rename at end
flag_value_over = 250

rename_cols = {'Tracking #':'Tracking Number',
  'Recipient':'Recipient Full Name'}

space = "     "
#This list will be the final headers, in order 
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
    if list(df.keys()) == final_col_order:
        print(f'     {file} is already a CBP manifest file, skipping... \n')
        return(False)
    try:
        df = df[keep_col].copy()
    except:
        print(f'     Incorrect headers for {file}. If {file} is not a stamps output, this is normal. If {file} is a stamps output, the headers may have changed. Adjust the names in keep_col above ' )
        print(f'     Skipping {file} \n')
        return(False)
    return(True)

def split_adress(order):
    order_adress = order["Recipient"].split(', ')
    if verbose: 
        print(f'\tParsing {order_adress}')
    if not order["Recipient"].endswith('US'): 
        name, *adress, city, state_plus_zip = order_adress
        country = 'US'
    else:
        name, *adress, city, state_plus_zip, country = order_adress
         
    state, zip_code = state_plus_zip.split(' ')
    adress  = ', '.join(adress)
    return(name, adress, city , state, zip_code, country)
 
def get_value(order):
    item_code = order['Printed Message']
    code_exsists = pd.isna(item_code)
    code_is_string = type(item_code) == str
    if verbose:
        print(f'\tGetting value for {item_code}')
    if not code_is_string or not code_exsists:
        return(pd.NA)
        item_value = search(r'\d*$', item_code).group()
    if item_value == '':
        return(pd.NA) 
        item_value = search(r'\d*$', item_code).group()
        return(float(item_value))
        
def remove_value(order):
    item_code = order['Printed Message']
    if verbose:
        print(f'\tRemoving value for {item_code}')
    if pd.isna(item_code):
        return(item_code)
    else:
        item_value = order[' Item 1 Value']
        new_code = item_code.strip(str(item_value))
        return(new_code)


csv_files = glob.glob('*.csv')
for file in csv_files:
    print(f"Working on {file}...\n ")
    file_name = file.split('.')[0]
    output_file = file_name + " Manifest.csv" 
    stamps_output = pd.read_csv(file, index_col=False) 
    #check that headers match expected stamps.com output 
    if not check_headers(stamps_output) == True:
        continue
    ##Pull values from item codes
    if verbose:
        print('Getting Values from codes...')
    stamps_output[' Item 1 Value'] = stamps_output.apply(get_value, axis = 1)
    if verbose:
        print('Getting Values from codes...')
    stamps_output['Item 1'] = stamps_output.apply(remove_value, axis = 1)
    #Parse Adresses  
    if verbose:
        print('Parsing Adresses...')
    new_addresses = stamps_output.apply(split_adress, axis = 1, result_type = 'expand')
    new_addresses.columns = recipient_headers
    stamps_output = stamps_output.drop(columns='Recipient')
    frames = [new_addresses, stamps_output]

    result = pd.concat(frames, axis=1)
    if verbose: 
        print('getting weights...')
    result['Weight'] = result['Weight'].str.split('lb', n=1,expand=True)[0].astype(int) +1
    
    #Rename some headers to CBP headers
    if verbose: 
        print('renaming cols to match CBP...')
    result = result.rename(rename_cols, axis = 1)
    result  = result.reindex(columns = final_col_order, fill_value = '')
    result['Lettermail?'] = 'N'
    result['Item 1 Qty'] = 1
    result['Item 1 Origin Country'] = 'US'   
    
    high_value_shipments = result[' Item 1 Value'] >= flag_value_over 
    no_code_shipments = result['Item 1'].isna()
    
    if high_value_shipments.any(): 
        hvs = [i+2 for i, x in enumerate(high_value_shipments) if x]
        print(f"\n\n\tWarning: the following lines have value >= {flag_value_over}: \n\t\t{hvs}\n\t\tDouble Check")
    if no_code_shipments.any(): 
        ncs = [i+2 for i, x in enumerate(no_code_shipments) if x]
        print(f"\n\n\tWarning: the following lines have no printed code or price : \n\t\t{ncs}\n\t\tAdd manually")
    try:   
        result.to_csv(output_file, index=False)
    except PermissionError:
        raise PermissionError('Could not write to csv file. If the file open in excel, close it. Then open after running script \n')

    print(f'\nDone {file} -> {output_file} \n')        


