#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 13 13:26:55 2020

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

# collecting data from API

"""
url = 'http://coronavirus-tracker-api.herokuapp.com/all'
url_iso2 = 'https://restcountries.eu/rest/v2/'


response_iso2 = requests.get(url_iso2)
lst_iso2 = json.loads(response_iso2.text)

response = requests.get(url)
lst = json.loads(response.text)

dict_pop = {}
dict_iso3 = {}
dict_affected = {}
dict_deaths = {}
dict_recovered = {}

for i in lst_iso2:
    dict_pop[i['alpha2Code']] = i['population']
    dict_iso3[i['alpha2Code']] = i['alpha3Code']
    dict_affected[i['alpha2Code']] = {}
    dict_deaths[i['alpha2Code']] = {}
    dict_recovered[i['alpha2Code']] = {}
      

## INITIALIZATION ##

for i in lst['confirmed']['locations']:
    code = i['country_code']
    if code in dict_iso3:
        for j in i['history']:
            dict_affected[code][j] = 0

for i in lst['recovered']['locations']:
    code = i['country_code']
    if code in dict_iso3:
        for j in i['history']:
            dict_recovered[code][j] = 0

for i in lst['deaths']['locations']:
    code = i['country_code']
    if code in dict_iso3:
        for j in i['history']:
            dict_deaths[code][j] = 0         


## Summing up ##

for i in lst['deaths']['locations']:
    name = i['country']
    code = i['country_code']
    if code in dict_iso3:
        for j in i['history']:
            dict_deaths[code][j] = dict_deaths[code][j] + i['history'][j] 

for i in lst['recovered']['locations']:
    name = i['country']
    code = i['country_code']
    if code in dict_iso3:
        for j in i['history']:
            dict_recovered[code][j] = dict_recovered[code][j] + i['history'][j] 

for i in lst['confirmed']['locations']:
    name = i['country']
    code = i['country_code']
    if code in dict_iso3:
        for j in i['history']:
            dict_affected[code][j] = dict_affected[code][j] + i['history'][j]                         



with open('country_model_new.csv', 'w') as csv_file:
    csv_writer = writer(csv_file)
    headers = ['Country_name', 'Country_code_iso2', 'Country_code_iso3', 'Date', 'Tot_affected', 'Tot_dead', 'Tot_recov', 'Population']
    csv_writer.writerow(headers)
    for i in lst['confirmed']['locations']:
        name = i['country']
        code = i['country_code']
        if code in dict_iso3:
            for j in i['history']:
                entry = [name, code, dict_iso3[code], j, dict_affected[code][j], dict_deaths[code][j], dict_recovered[code][j], dict_pop[code]]
                csv_writer.writerow(entry)
"""

# data collection stops; let's import it and save it on X
with open('country_model_new.csv', 'rb') as f:
    result = chardet.detect(f.read())  # or readline if the file is large

dataset = pd.read_csv('country_model_new.csv', keep_default_na=False,  encoding=result['encoding'])
X = dataset.iloc[:, :].values

#%%
#----------fixing date (Y-m-d)---------
from datetime import datetime as dt, timedelta
for i in range(len(X)):
    # print(i)
    yesterday_str = X[i][3]
    yesterday = dt.strptime(yesterday_str, '%m/%d/%y').date()
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    X[i][3] = yesterday_str

temp1 = np.array(np.ones((len(X),1)))
temp1 = X[:,4] - (X[:,5] + X[:,6])
temp1 = temp1.reshape((len(X),1))
X = np.hstack((X[:, :7], temp1, X[:, 7:]))

#%%
#------delteing extra data----------
# from extra, comes extra new datas -_-
# now let's delete repeating datas
country_data = (X == "Bangladesh").sum()
# country_data = 105

extra = country_data * 230
X = np.delete(X, slice(extra, len(X)), 0)

flag = []
i = 0
while i < len(X):
    j = i+country_data
    while j < len(X):
        if X[i][0] == X[j][0] and flag.count(j) == 0:
            flag.append(j)
        j = j + country_data
    i = i + country_data 
   
flag.reverse()
for i in flag:
    X = np.delete(X, slice(i, i+country_data), 0)
# total country should be 161    
#%%
# 3rd part : calculation
codeList = []
i = 0
while i < len(X):
    #40 threshold set as total cases to avoid unexpected results
    # if X[i+country_data-1][4] >= 40 and X[i][0] != "Serbia":
    codeList.append(X[i][1])
    i = i + country_data

# code = codeList[80]     #to test
codeIndex = 1
report = np.empty((0, 8), object)
idx = 0
#--------------looping starts-----------
# code = 'MN'
for code in itertools.islice(codeList, 0, len(codeList)):
    datas = 0
    # arr: country data by dates
    # datas: number of countries
    arr = np.empty((country_data, 9), dtype=object)
    for row in X:
        if row[codeIndex] == code : 
            arr[datas]=row
            datas = datas+ 1
    print(arr[0][0])
     
    arr = arr[np.argsort(arr[:,3])]
    # init: previous values (0 for dead, 1 for affected)
    init = np.empty((datas, 2), dtype=object)
    init[0][0] = arr[0][5]
    init[0][1] = arr[0][4]
    for i in range(1, datas):
        init[i][0] = arr[i][5] - arr[i-1][5]
        init[i][1] = arr[i][4] - arr[i-1][4]
    # for last 2 equations of SIRD
    def calLamda(D):
        lst = []
        for i in range(len(arr) - 1):
            l = 0
            if D == True:
                if arr[i][7] != 0 :     #divide by zero!
                    l = (arr[i+1][5] - arr[i][5]) / arr[i][7]       #lamdaD=(D1 - D0)/ Id0
            else:
                if arr[i][7] != 0 :     #divide by zero!
                    l = (arr[i+1][6] - arr[i][6]) / arr[i][7]       #lamdaR=(R1 - R0)/ Ir0
            if arr[i][3] >= "2020-03-05":                           #timing considered from March 05 to see its growing shape
                lst.append(l)
        return lst
    
    lamdaD = calLamda(True)
    lamdaR = calLamda(False)
    # last 5 values average taken as constant
    ld = mean(lamdaD[-5:])
    # print(ld)
    lr = mean(lamdaR[-5:])
    # print(lr)    
    
    lstBSbyL = []
    for i in range(len(arr) - 1):
        #BS0 = ((Id1 + Ir1 + Id0*lamdaD + Ir0*lamdaR) - (Id0 + Ir0)) / (Id0 + Ir0)
        l = 0
        fplus = arr[i+1][7] + arr[i][7]*(ld + lr)
        splus = arr[i][7]
        if splus != 0:
            l = (fplus - splus)/ splus    
        if arr[i][3] >= "2020-03-05":                           #timing considered from March 05 to see its growing shape
            lstBSbyL.append(l)            
    # last 5 values average taken as constant
    lbsl = mean(lstBSbyL[-5:])
    # print(lbsl/ (ld + lr))
    
    # pop: population of corresponding country
    for i in range(len(X)):
        if X[i][codeIndex] == code:
            pop = X[i][8]
            # print(pop)
            break
    # number of confirmed cases subtracted from actual population
    pop = pop - arr[-1][4]
    # now some hardcoding max, min, average bullshit begins!!
    minConst = 50
    maxConst = 1800
    midConst = 300
    pop1 = pop / minConst
    beta1 = (lbsl / pop1)
    
    pop3 = pop / maxConst
    beta3 = (lbsl / pop3)
    
    pop2 = pop / midConst
    beta2 = (lbsl / pop2)
    
    # here goes our incremental SIRD model; (Eliza, try an ODE version? I haven't tried)
    # this function returns future daily affecteds or deads
    def calcDiff(pop, beta):
        final = np.empty((30, 4), dtype=object)
        final[0][0] = pop - beta*pop*arr[-1][7]                             #S
        final[0][1] = arr[-1][7] + beta*pop*arr[-1][7] - (ld+lr)*arr[-1][7] #I
        final[0][2] = arr[-1][6] + lr*arr[-1][7]                            #R
        final[0][3] = arr[-1][5] + ld*arr[-1][7]                            #D
        
        for i in range(1, len(final)):
            final[i][0] = final[i-1][0] - beta*final[i-1][0]*final[i-1][1]
            final[i][1] = final[i-1][1] + beta*final[i-1][0]*final[i-1][1] - (ld+lr)*final[i-1][1]
            final[i][2] = final[i-1][2] + lr*final[i-1][1]
            final[i][3] = final[i-1][3] + ld*final[i-1][1]
            
        final[:, [0,1,2,3]] = final[:, [0,1,2,3]].astype(int)    
        final = np.append(final, np.ones((len(final),1)), axis = 1)
        final[:,4] = final[:,1] + final[:,2] + final[:,3]                   #cases=active+R+D
        
        diffDead=[]
        diffDead.append(abs(final[0][3] - arr[-1][5]))
        for i in range(1,len(final)):
            diffDead.append(final[i][3] - final[i-1][3])        
        diffAffec=[]
        diffAffec.append(abs(final[0][4] - arr[-1][4]))
        for i in range(1,len(final)):
            diffAffec.append(final[i][4] - final[i-1][4])
       
        return (diffAffec, diffDead)
    
    dA1, dD1 = calcDiff(pop1, beta1)
    dA2, dD2 = calcDiff(pop2, beta2)
    dA3, dD3 = calcDiff(pop3, beta3)
    
    """    
    #ploting stuffs
    # init[:,0]-> dead, 1-> affected; change dA-> for dead
    prevVals = init[:,1]
    x = np.arange(datas, datas+30) 
    plt.plot(prevVals, color = 'b')
    plt.plot(x,dA1, '--', color = 'r')    
    plt.plot(x,dA2, '--', color = 'black')
    plt.plot(x,dA3, '--', color = 'r')
    plt.title(f"{arr[0][0]}")
    plt.show()
    """  
    # now lets create our report, which will be pushed into database
    name = arr[0][0]
    name = np.full((30,1), name)
    code2 = arr[0][1]
    code2 = np.full((30,1), code2)
    
    one_day = timedelta(days = 1)
    yesterday_str = arr[-1][3]
    yesterday = dt.strptime(yesterday_str, '%Y-%m-%d').date()
    Today = np.full((30,1), yesterday_str)
    
    day_predict = []
    for i in range(30):
        day = yesterday + one_day
        yesterday = day
        day = day.strftime("%Y-%m-%d")
        day_predict.append(day)
    day_predict = np.array(day_predict)
    day_predict = day_predict.reshape((30,1))
    
    def createReport (string, v1, v2, v3):
        Type = np.full((30,1), string)        
        v1 = np.array(v1)
        v2 = np.array(v2)
        v3 = np.array(v3)
        v1 = v1.reshape((30,1))
        v2 = v2.reshape((30,1))
        v3 = v3.reshape((30,1))   
        values = np.hstack((Type, name, code2, Today, day_predict, v2, v1, v3))
        values = values.reshape((30, 8))
        return values
    
    reportAffec = createReport("Affected", dA1, dA2, dA3)
    reportDead = createReport("Dead", dD1, dD2, dD3)
    report = np.vstack((report[:idx, :], reportAffec, reportDead, report[idx+60:, :]))
    idx = idx + 60
noCountries = int(len(report)/60)

"""
report
0-> type (affected/ dead)
1-> country_name
2-> code2
3-> database pushing date
4-> prediction date
5-> middle val
6-> max val
7-> min val
"""

#%%

tot_countries = noCountries
dbase = np.empty(((tot_countries, 11)), dtype = object)

# j = 0
i = country_data-1
for j in range(noCountries):
    # print(i)
    dbase[j][0] = X[i][0]
    dbase[j][1] = X[i][2]
    dbase[j][2] = X[i][3]
    dbase[j][3] = X[i][4] - X[i-1][4]
    dbase[j][4] = X[i][5] - X[i-1][5]
    j = j+1
    i = i + country_data
    
i = 0
for j in range(noCountries):
    dbase[j][5] = report[i][4]
    dbase[j][6] = report[i][4+2]
    dbase[j][7] = report[i+30][4+2]
    dbase[j][8] = report[i+1][4]
    dbase[j][9] = report[i+1][4+2]
    dbase[j][10] = report[i+30][4+2]
    i= i+60

"""
dbase[:,0] = country
dbase[:,1] = code
dbase[:,2] = date_yesterday
dbase[:,3] = affected_yesterday
dbase[:,4] = death_yesterday
dbase[:,5] = date_today
dbase[:,6] = affected_today
dbase[:,7] = death_today
dbase[:,8] = date_tomorrow
dbase[:,9] = affected_tomorrow
dbase[:,10] = death_tomorrow
"""
