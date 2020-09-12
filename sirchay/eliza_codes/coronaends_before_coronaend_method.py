#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 17:23:49 2020

@author: hisham
"""


import chardet
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import requests
import json
from flask import jsonify
from csv import writer
from statistics import mean
import itertools
import psycopg2
import plotly.graph_objects as go
import psycopg2
from datetime import datetime as dt, timedelta

"""
url = 'http://coronavirus-tracker-api.herokuapp.com/all'
url_iso2 = 'https://restcountries.eu/rest/v2/'

url_new_pref = 'https://covid19-api.org/api/timeline/'

response_iso2 = requests.get(url_iso2)
lst_iso2 = json.loads(response_iso2.text)

# response = requests.get(url)
# lst = json.loads(response.text)
dict_name = {}
dict_pop = {}
dict_iso3 = {}
dict_affected = {}
dict_deaths = {}
dict_recovered = {}
dict_timeline = {}

responses = []


with open('country_model_newApi.csv', 'w', newline='') as csv_file:
    csv_writer = writer(csv_file)
    headers = ['Country_name', 'Country_code_iso2', 'Country_code_iso3', 'Date', 'Tot_affected', 'Tot_dead', 'Tot_recov', 'Population']
    csv_writer.writerow(headers)
    for i in lst_iso2:
        # print(i['name'], i['population'])
        # dict_name[i['alpha2Code']] = i['name']
        # dict_iso3[i['alpha2Code']] = i['alpha3Code']
        iso2 = i['alpha2Code']
        iso3 = i['alpha3Code']
        name = i['name']
        print(name)
        population = i['population']
        res = requests.get(url_new_pref + iso2)
        lst_res = json.loads(res.text)
        if(len(lst_res) > 0):
            dict_timeline[iso2] = lst_res
            # print(lst_res[0]['country'])
            # print(i['name'], lst_res[0])
            for j in lst_res:
                entry = [name, iso2, iso3, j['last_update'].split('T')[0], j['cases'], j['deaths'], j['recovered'], population]
                csv_writer.writerow(entry)
"""
# data collection stops; let's import it and save it on X
with open('country_model_newApi.csv', 'rb') as f:
    result = chardet.detect(f.read())  # or readline if the file is large

dataset = pd.read_csv('country_model_newApi.csv', keep_default_na=False,  encoding=result['encoding'])
X = dataset.iloc[:, :].values

#%%
country_data = (X == "Spain").sum()


temp1 = np.array(np.ones((len(X),1)))
temp1 = X[:,4] - (X[:,5] + X[:,6])
temp1 = temp1.reshape((len(X),1))
X = np.hstack((X[:, :7], temp1, X[:, 7:]))


#%%

# 3rd part : calculation
codeList = []
i = 0
t = dt.today() - timedelta(days = 1)
t = t.strftime("%Y-%m-%d")
while i < len(X):
    #40 threshold set as total cases to avoid unexpected results
    if X[i][3] == t and X[i][4] >= 40 and X[i][0] != "Serbia" and X[i][0]!= "Antigua and Barbuda" and X[i][0]!= "Sweden" and X[i][0]!= "United Kingdom" and X[i][0]!= "France" :
        codeList.append(X[i][1])
    i = i + 1
# print(len(codeList) == len(set(codeList)))
codeIndex = 1
report = np.empty((0, 8), object)
idx = 0


code = 'IN'

