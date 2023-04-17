# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 13:45:24 2022

@author: Mark Zanon

Converts stamps.com output to crossborder manifest.


Instructions: Export csv file from stamps and put that file in the same directory as this script. Running the script will create a new csv file with a similar name as the stamps file. The name does not matter as long as it is a .csv file
If there are multiple .csv files, this script will try and create a manifest for each.  
"""

#TODO: Add logging function for verbose debugging
#FIXME: Figure out what is wrong with the string thing 

verbose = False
#imports
import pandas as pd 
import sys
import glob
import csv
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

states = {"AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California","CO":"Colorado","CT":"Connecticut","DE":"Delaware","FL":"Florida","GA":"Georgia","HI":"Hawaii","ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland","MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina","ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia","WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming"}
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
    adress  = ' '.join(adress)
    return(name, adress, city , state, zip_code, country)
 
def get_value(order):
    item_code = order['Printed Message']
    code_is_nan = pd.isna(item_code)
    code_is_string = type(item_code) == str
    if verbose:
        print(f'\tGetting value for {item_code}')
    if not code_is_string or code_is_nan:
        return(pd.NA)
    item_value = search(r'\d*$', item_code).group()
    if item_value == '':
        return(pd.NA) 
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

def print_warning(pdBool, error_type):
    orders_with_errors = [index+2 for index, has_error in enumerate(pdBool) if has_error]
    errors = {"high_value": 
                  f"\n\n\tWarning: the following lines have value >= {flag_value_over}: \n\t\t{orders_with_errors}\n\t\tDouble Check",
              "no_code":
                  f"\n\n\tWarning: the following lines have no printed code: \n\t\t{orders_with_errors}\n\t\tAdd manually",
              'no_price':
                  f"\n\n\tWarning: Price not detecteed for the following lines \n\t\t{orders_with_errors}\n\t\tAdd manually",
              'no_state':f"\n\n\tWarning: Following lines do not have valid US states: \n\t\t{orders_with_errors}\n\t\t"}
    print(errors[error_type])

def check_tracking_numbers(order):
    tracking_number = order['Tracking Number']
    return(tracking_number)
    # tracking_number = str(order['Tracking Number'])
    # if type(tracking_number) == str:
        # tracking_number = ''.join(["=\"",tracking_number,'\"'])
    # return(tracking_number)


csv_files = glob.glob('*.csv')
for file in csv_files:
    print(f"Working on {file}...\n ")
    file_name = file.split('.')[0]
    output_file = file_name + " Manifest.csv" 
    try:
        stamps_output = pd.read_csv(file, index_col=False) 
    except:
        print("could parse {file}, headers may be wrong. Skipping...")
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
            # result['Tracking Number'] = result.apply(check_tracking_numbers, axis = 1)
    result['Tracking Number'] = '="'+result["Tracking Number"]+'"' 
    #Find misbehaving orders
    high_value = result[' Item 1 Value'] >= flag_value_over 
    no_code = result['Item 1'].isna()
    no_price = result[' Item 1 Value'].isna()
    no_state = ~result['State'].isin(states)
    # no_state = [bool(x) for x in result["State"] if not x in states]
    
    errors = {'high_value':high_value, 'no_code':no_code, "no_price":no_price, "no_state":no_state}
    #cry wolf
    for error_type, orders_with_problems in errors.items():
        if orders_with_problems.any():
            print_warning(orders_with_problems, error_type)

    try:   
        result.to_csv(output_file, index=False, quoting=csv.QUOTE_MINIMAL)
    except PermissionError:
        raise PermissionError('Could not write to csv file. If the file open in excel, close it. Then open after running script \n')

    print(f'\nDone {file} -> {output_file} \n')        


