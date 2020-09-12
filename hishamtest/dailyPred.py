#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 21:31:02 2020

@author: hisham
"""

# import math
import requests
import json
from flask import jsonify
from csv import writer
import csv
import unicodecsv
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

url = 'https://corona-api.com/countries/'
url_iso2 = 'https://restcountries.eu/rest/v2/'

querystring = {"country":"Bangladesh"}

headers = {
    'x-rapidapi-host': "coronavirus-monitor.p.rapidapi.com",
    'x-rapidapi-key': "b23312c441msh260b60b1bd6e484p1f47f7jsnd56b11696dd9"
    }

response_iso2 = requests.get(url_iso2)
lst_iso2 = json.loads(response_iso2.text)

with open('country_timeline1.csv', 'w') as csv_file:
    csv_writer = writer(csv_file)
    headers = ['Country_name', 'Country_code_iso2', 'Country_code_iso3', 'Date', 'New_confirmed', 'New_deaths']
    csv_writer.writerow(headers)
    for i in lst_iso2:
        # print(i['alpha2Code'])
        country_name = i['name']
        country_code2 = i['alpha2Code']
        country_code3 = i['alpha3Code']
        lnk = url + country_code2
        # print(lnk)
        response = requests.get(lnk)
    

        lst = json.loads(response.text)
        # print(country_code)
        if 'data' in lst:
            if(len(lst['data']['timeline']) > 0):
                for j in lst['data']['timeline']:
                    date = j['date']
                    new_confirmed = j['new_confirmed']
                    new_deaths = j['new_deaths']
                    # print(country_code, date, new_confirmed, new_deaths)
                    entry = [country_name, country_code2, country_code3, date, new_confirmed, new_deaths]
                    csv_writer.writerow(entry)
                    
                    

dataset = pd.read_csv('country_timeline1.csv', keep_default_na=False)
X = dataset.iloc[:, :].values
Z = dataset.iloc[0:540, :].values
# Z = Z.reshape((4,600))
print(X)
print(Z)


i = 0
for row in X:
    # print(row)
    if row[3] == '2020-04-15':
        # print(row)
        Z[i] = row
        i = i + 1
# print(i)
for row in X:
    if row[3] == '2020-04-14':
        Z[i] = row
        i = i + 1
# print(i)
for row in X:
    if row[3] == '2020-04-13':
        Z[i] = row
        i = i + 1
# print(i)

# Z = np.delete(Z, 293, axis = 0)
# Z = np.delete(Z, 472, axis = 0)

# for i in range(180, 360):
#     val = True
#     for j in range(180):
#         if Z[j][0] == Z[i][0]:
#             val = False 
#     if val == True:
#         print(i)
#         print(Z[i][0])

# for i in range(180):
#     # print(Z[i][0])
#     if (Z[i][0] != Z[i+180][0]) or (Z[i][0] != Z[i+360][0]):
#         print(Z[i][0])
        
new = Z
new = np.append(new, np.zeros((540,4)), axis = 1)

for i in range(180):
    new[i][4] = new[i+180][2]
    new[i][5] = new[i+180][3]
    new[i][6] = new[i+2*180][2]
    new[i][7] = new[i+2*180][3]
    
new = np.append(new, np.zeros((540,4)), axis = 1)

top = new


for i in range(len(top)):
    if top[i][2] > top[i][4] and top[i][4] > top[i][6]:
        top[i][8] = top[i][2] + (top[i][2] - top[i][6])/4 - (top[i][4] - top[i][6])/3
        if top[i][8] < 0:
            top[i][8] = 0
    elif top[i][2] < top[i][4] and top[i][4] < top[i][6]:   
        top[i][8] = top[i][2] - (top[i][6] - top[i][2])/4 + (top[i][6] - top[i][4])/3 
        if top[i][8] < 0:
            top[i][8] = 0
    else:
        top[i][8] = (top[i][2] + top[i][4] + top[i][6])/3
        

for i in range(len(top)):
    if top[i][3] > top[i][5] and top[i][5] > top[i][7]:
        
        top[i][9] = top[i][3] + (top[i][3] - top[i][7])/4 - (top[i][5] - top[i][7])/3
        if top[i][9] < 0:
            top[i][9] = 0
        
    elif top[i][5] < top[i][2] and top[i][2] < top[i][3]:
        
        top[i][9] = top[i][3] - (top[i][7] - top[i][3])/4 + (top[i][7] - top[i][5])/3
        if top[i][9] < 0:
            top[i][9] = 0
    else:
        top[i][9] = (top[i][5] + top[i][2] + top[i][3])/3

for i in range(len(top)):
    if top[i][8] > top[i][2] and top[i][2] > top[i][4]:
        
        top[i][10] = top[i][8] + (top[i][8] - top[i][4])/4 - (top[i][2] - top[i][4])/3
        if top[i][10] < 0:
            top[i][10] = 0
    elif top[i][8] < top[i][2] and top[i][2] < top[i][4]:
        
        top[i][10] = top[i][8] - (top[i][4] - top[i][8])/4 + (top[i][4] - top[i][2])/3
        if top[i][10] < 0:
            top[i][10] = 0
    else:
        top[i][10] = (top[i][8] + top[i][2] + top[i][4])/3
        
for i in range(len(top)):
    if top[i][9] > top[i][3] and top[i][3] > top[i][5]:
        
        top[i][11] = top[i][9] + (top[i][9] - top[i][5])/4 - (top[i][3] - top[i][5])/3
        if top[i][11] < 0:
            top[i][11] = 0
    elif top[i][9] < top[i][3] and top[i][3] < top[i][5]:
        
        top[i][11] = top[i][9] - (top[i][5] - top[i][9])/4 + (top[i][5] - top[i][3])/3
        if top[i][11] < 0:
            top[i][11] = 0
    else:
        top[i][11] = (top[i][9] + top[i][3] + top[i][5])/3
        
# top = np.around(top[:, 8])
temp = top[:, [8,9,10,11]]
temp = temp.astype(float)
# print(np.around(temp))
temp = np.around(temp)
top[:, [8,9,10,11]] = temp
top[:, [8,9,10,11]] = top[:, [8,9,10,11]].astype(int)

temp = top[0:180, 8]
temp = temp.reshape((len(temp), 1))

np.savetxt("country.txt", top[0:180, 0], fmt="%s", newline="\",\"")
np.savetxt("d-1A.txt", top[0:180, 2], fmt="%s", newline=",")
np.savetxt("d-1D.txt", top[0:180, 3], fmt="%s", newline=",")
np.savetxt("dA.txt", top[0:180, 8], fmt="%s", newline=",")
np.savetxt("dD.txt", top[0:180, 9], fmt="%s", newline=",")
np.savetxt("d+1A.txt", top[0:180, 10], fmt="%s", newline=",")
np.savetxt("d+1D.txt", top[0:180, 11], fmt="%s", newline=",")
print(top)
# np.appendtxt("output1.txt", temp, fmt="%s", newline=",")