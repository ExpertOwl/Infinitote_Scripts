"""
@author: ExpertOwl/Mark 

Purpose: 
    Create SKUs from toady's date':
    e.g. 0ABC-2041
    Desired format is: 
        random digit + 3 random letters + dash + 2-digit year code + 2-digit week code    
"""
from random import choice as choose_one_from
from datetime import date

valid_letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
valid_numbers = list('0123456789')

def make_sku():
    iso_date = date.today().isocalendar()
    formatted_date_code = generate_date_code(iso_date) 
    formatted_alphanum_part = generate_alphanumeric_part()
    formatted_sku = f"{formatted_alphanum_part}-{formatted_date_code}"
    return(formatted_sku)
           
def generate_date_code(iso_date):
    iso_year = str(iso_date[0])
    iso_week = str(iso_date[1])
    year_code = get_last_two_digits_and_zfill(iso_year)
    week_code = get_last_two_digits_and_zfill(iso_week)
    formatted_date_code = f"{year_code}{week_code}"
    return(formatted_date_code)

def get_last_two_digits_and_zfill(string):
    string = string[-2:]
    string.zfill(2)
    return(string)

def generate_alphanumeric_part():
    random_letters = choose_three_random_letters()
    random_number = choose_one_valid_number()
    formatted_alphanum = f"{random_number}{random_letters}"
    return(formatted_alphanum)

def choose_three_random_letters(letters_to_chose_from = valid_letters):
    chosen_letters = []
    for i in range(3):
        chosen_letters.append(choose_one_from(letters_to_chose_from))
    chosen_letters_as_string = ''.join(chosen_letters)
    return(chosen_letters_as_string)

def choose_one_valid_number(numbers_to_choose_from = valid_numbers):
    random_number = choose_one_from(numbers_to_choose_from)
    return(random_number)

sku = make_sku()
print(sku)
