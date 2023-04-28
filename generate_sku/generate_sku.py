# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 13:45:24 2022

@author: ExpertOwl/Mark 
Generates random date code to create SKUs. [Digit][Letter][Letter][Letter][yr][week]
"""
from random import choice as pick
from pyperclip import copy as clipboard
from datetime import date

letters=list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
numbers=list('0123456789')

def make_sku():
    year, week, day = date.today().isocalendar()
    yearcode = str(year)[2:]
    week = str(week).zfill(2) #Add zeroes if needed (1 -> 01)
    randletters =''.join(pick(letters) for i in range(3))
    randnumber = pick(numbers)
    return(f'{randnumber}{randletters}-{yearcode}{week}')

def ft(string):
    formatted_string = string.split(', ')
    print("\n".join(formatted_string))
sku = make_sku()
clipboard(sku)
print(f'\n {sku} copied to clipboard')
