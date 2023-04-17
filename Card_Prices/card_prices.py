# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 12:13:47 2022

@author: user
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def kahanSum(fa):
    sum = 0.0
    c = 0.0

    for f in fa:
        y = f - c
        t = sum + y

        c = (t - sum) - y
        sum = t
 
    return sum

def xGivenN(n):
    return(np.log(n + 1)/np.log(32/31))

npoints = 200
p0 = (1/4*1/8)
kmax = np.linspace(0,200, num = npoints)
ch_8_6=28
def pComplete(kmax, p0 = p0):
    plastcard = p0 * (1-p0)**(kmax - 1) 
    p_7_cards = (1-(1-p0)**kmax)**7
    return (8*plastcard * p_7_cards)



pk = pComplete(kmax)



mean = kahanSum(pk*kmax)
print(mean)
var = sum(pComplete(kmax**2)) - sum(pComplete(kmax)**2)
plt.figure()
plt.plot(kmax, pk*100)
plt.xlabel('Number of cards crafted')
plt.ylabel('Chance of completing the nobles deck')
plt.axvline(mean, linestyle = '--', color = 'k')
# plt.axvline(most_likley_prob, linestyle = '--', color = 'r')

plt.legend(['P_{complete}(K)$', f'Mean = {mean}'] )

plt.figure()
plt.plot(kmax, np.cumsum(pk))
plt.xlabel('Number of cards crafted')
plt.ylabel('Cumulative probability of completing the nobles deck')
plt.axvline(mean, linestyle = '--', color = 'k')
# plt.axvline(most_likley_prob, linestyle = '--', color = 'r')
plt.legend(['$\Sigma_i P_{complete}(K_i)$', 'Mean = 72.32', "Most likley = 53.5"] )


n=np.linspace(0,8,num=9)
print(xGivenN(n))

# """
# To craft one card, need 6 snowfall ink 3 eternal life and 3 ink of the sea 
# 1 snowfall ink = 10 ink of the sea so really we need 6*10+3 (63) ink of the sea or 6.3 snowfall ink

# 12.6 azure pigments or 126 icy pigment

# Let's base it off azure pigment because those are the limiting reagent anyway'

Herbs = ['Goldclover', 
          'Tigers Lily', 
          "Talandras Rose",
          'Deadnettle', 
          'Fireleaf', 
          'Adders Tongue', 
          'Litchbloom', 
          'Icethorn',]

price_herb = [0.20, 0.30, 1.51, 1.43, 1.58,2.58,2.45,2.35]
price_mil = [price * 5 for price in price_herb]

#Average pigments per mill 
icy = [0.25+2.5/10, 0.25+2.5/10, 0.25+2.5/10, 0.25+2.5/10, 0.25+2.5/10, 0.5+3/10, 0.5+3/10, 0.5+3/10]

data = pd.DataFrame([price_mil, icy], columns = Herbs, index = ['Price', "Icy"])

mills_per_card = np.asarray([12.6/pigment_rate for pigment_rate in icy])

price_per_card = data.T['Price'] * mills_per_card
price_per_pigment = data.T['Price']/data.T['Icy']

data['Price per card'] = price_per_card

print(f'Price per pigment: \n \n{price_per_pigment} \n')
print(f'price_per_card: \n \n{price_per_pigment * 12}\n')
print(f'Herbs needed per card:\n \n{price_per_pigment * 12 /price_herb}')

