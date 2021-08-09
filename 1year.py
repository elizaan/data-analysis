#!/usr/bin/env python
# coding: utf-8

# In[9]:


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 17:18:07 2020
@author: hisham
"""


import chardet
import math
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
import sys 
from datetime import datetime as dt, timedelta
# import plotly.graph_objects as go

url = 'http://coronavirus-tracker-api.herokuapp.com/all'
url_iso2 = 'https://restcountries.eu/rest/v2/'

# print("hello working")

# %%
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
    headers = ['Country_name', 'Country_code_iso2', 'Country_code_iso3',
               'Date', 'Tot_affected', 'Tot_dead', 'Tot_recov', 'Population']
    csv_writer.writerow(headers)
    for i in lst['confirmed']['locations']:

        name = i['country']
        code = i['country_code']
        if code in dict_iso3:
            #prevDate = ''
            for j in i['history']:
                entry = [name, code, dict_iso3[code], j, dict_affected[code][j],
                         dict_deaths[code][j], dict_recovered[code][j], dict_pop[code]]
                #entry = [name, code, dict_iso3[code], j, dict_affected[code][j], dict_deaths[code][j], dict_recovered[code].get(j,prevDate), dict_pop[code]]
                #s = j.split('/')
                #prevDate = s[0] + '/' + str(int(s[1]) - 1) + '/' + s[2]
                csv_writer.writerow(entry)

# %%
with open('country_model_new.csv', 'rb') as f:
    result = chardet.detect(f.read())  # or readline if the file is large

dataset = pd.read_csv('country_model_new.csv',
                      keep_default_na=False,  encoding=result['encoding'])
X = dataset.iloc[:, :].values

# %%
# ----------fixing date (Y-m-d)---------
for i in range(len(X)):
    # print(i)
    yesterday_str = X[i][3]
    yesterday = dt.strptime(yesterday_str, '%m/%d/%y').date()
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    X[i][3] = yesterday_str

temp1 = np.array(np.ones((len(X), 1)))
temp1 = X[:, 4] - (X[:, 5] + X[:, 6])
temp1 = temp1.reshape((len(X), 1))
X = np.hstack((X[:, :7], temp1, X[:, 7:]))

# %%
# ------delteing extra data----------
# from extra, comes extra new datas -_-
# now let's delete repeating datas
country_data = (X == "Bangladesh").sum()
#print(country_data)
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

# %%
# 3rd part : calculation
codeList = []
i = 0
while i < len(X):
    # 40 threshold set as total cases to avoid unexpected results
    if X[i+country_data-1][4] >= 40 and X[i][0] != "Serbia" and X[i][0] != "Antigua and Barbuda":
        codeList.append(X[i][1])
    i = i + country_data

# code = codeList[80]     #to test
codeIndex = 1
report = np.empty((0, 8), object)
idx = 0

# %%
# country_data = (X == "Spain").sum()
# temp1 = np.array(np.ones((len(X),1)))
# temp1 = X[:,4] - (X[:,5] + X[:,6])
# temp1 = temp1.reshape((len(X),1))
# X = np.hstack((X[:, :7], temp1, X[:, 7:]))

# %%

# 3rd part : calculation
# codeList = []
# i = 0
# t = dt.today() - timedelta(days = 1)
# t = t.strftime("%Y-%m-%d")
# while i < len(X):
#     #40 threshold set as total cases to avoid unexpected results
#     if X[i][3] == t and X[i][4] >= 100:
#         codeList.append(X[i][1])
#     i = i + 1
# # print(len(codeList) == len(set(codeList)))
# codeIndex = 1
# report = np.empty((0, 8), object)
# idx = 0


code = 'IN'

t = dt.today() - timedelta(days=1)
t = t.strftime("%Y-%m-%d")
for code in itertools.islice(codeList, 0, len(codeList)):
    datas = 0
    # arr: country data by dates
    # datas: number of countries
    # country_data = (X == code).sum()
    country_data = 0
    for row in X:
        if row[codeIndex] == code and row[3] <= t:
            country_data += 1
    arr = np.empty((country_data, 9), dtype=object)

    for row in X:
        if row[codeIndex] == code and row[3] <= t:
            arr[datas] = row
            datas = datas + 1
    # print(arr[0][0])
    arr = arr[np.argsort(arr[:, 3])]

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
                if arr[i][7] != 0:  # divide by zero!
                    l = (arr[i+1][5] - arr[i][5]) / \
                        arr[i][7]  # lamdaD=(D1 - D0)/ Id0
            else:
                if arr[i][7] != 0:  # divide by zero!
                    l = (arr[i+1][6] - arr[i][6]) / \
                        arr[i][7]  # lamdaR=(R1 - R0)/ Ir0
            if arr[i][3] >= "2020-03-05":  # timing considered from March 05 to see its growing shape
                if l < 0:
                    l = 0  # to avoid unpredented results
                lst.append(l)
        return lst

    lamdaD = calLamda(True)
    lamdaR = calLamda(False)
    days_to_take = 8
    # last 'days_to_take' values average taken as constant
    ld = mean(lamdaD[-days_to_take:])
    # print(ld)
    lr = mean(lamdaR[-days_to_take:])
    # print(lr)
    lstBSbyL = []
    for i in range(len(arr) - 1):
        #BS0 = ((Id1 + Ir1 + Id0*lamdaD + Ir0*lamdaR) - (Id0 + Ir0)) / (Id0 + Ir0)
        l = 0
        fplus = arr[i+1][7] + arr[i][7]*(ld + lr)
        splus = arr[i][7]
        if splus != 0:
            l = (fplus - splus) / splus
        if arr[i][3] >= "2020-03-05":  # timing considered from March 05 to see its growing shape
            lstBSbyL.append(l)
    # last 5 values average taken as con'stant
    lbsl = mean(lstBSbyL[-days_to_take:])
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
    maxconst = 300
    midconst = 60
    minconst = 10
    pop1 = pop / minconst
    beta1 = (lbsl / pop1)
    pop3 = pop / maxconst
    beta3 = (lbsl / pop3)
    pop2 = pop / midconst
    beta2 = (lbsl / pop2)

    # here goes our incremental SIRD model; (Eliza, try an ODE version? I haven't tried)
    # this function returns future daily affecteds or deads
    def calcDiff(pop, beta):
        # print("pop,beta,array[-1][7]" )
        # print(pop,beta,arr[-1][7])
        final = np.empty((360, 4), dtype=object)
        lame = np.empty(360, dtype=object)
        lame2 = np.empty(360, dtype=object)
        final[0][0] = pop - beta*pop*arr[-1][7]  # S
        final[0][1] = arr[-1][7] + beta*pop * \
            arr[-1][7] - (ld+lr)*arr[-1][7]  # I
        final[0][2] = arr[-1][6] + lr*arr[-1][7]  # R
        final[0][3] = arr[-1][5] + ld*arr[-1][7]  # D

        for i in range(1, len(final)):
            final[i][0] = final[i-1][0] - beta*final[i-1][0]*final[i-1][1]
            final[i][1] = final[i-1][1] + beta*final[i-1][0] * \
                final[i-1][1] - (ld+lr)*final[i-1][1]
            final[i][2] = final[i-1][2] + lr*final[i-1][1]
            final[i][3] = final[i-1][3] + ld*final[i-1][1]
            # print(final[i][0],final[i][1],final[i][2],final[i][3])

            if final[i][0] > sys.maxsize or final[i][1] > sys.maxsize or final[i][2] > sys.maxsize or final[i][3] > sys.maxsize:
                final[i][0] = 0
                final[i][1] = 0
                final[i][2] = 0
                final[i][3] = 0
            if np.isnan(final[i][0]) or np.isnan(final[i][1]) or np.isnan(final[i][2]) or np.isnan(final[i][3]) or math.isinf(final[i][0]) or math.isinf(final[i][1]) or math.isinf(final[i][2]) or math.isinf(final[i][3]):

                final[i][0] = 0
                final[i][1] = 0
                final[i][2] = 0
                final[i][3] = 0

        final[:, [0, 1, 2, 3]] = final[:, [0, 1, 2, 3]].astype('int64')
        final = np.append(final, np.ones((len(final), 1)), axis=1)
        final[:, 4] = final[:, 1] + final[:, 2] + \
            final[:, 3]  # cases=active+R+D

        diffDead = []
        diffDead.append(abs(final[0][3] - arr[-1][5]))
        for i in range(1, len(final)):

            if (final[i][3] - final[i-1][3]) < 0:
                lame[i] = final[i][3] - final[i-1][3]
                lame[i] = 0
                diffDead.append(lame[i])

            else:
                diffDead.append(final[i][3] - final[i-1][3])
        diffAffec = []
        diffAffec.append(abs(final[0][4] - arr[-1][4]))
        for i in range(1, len(final)):

            if (final[i][4] - final[i-1][4]) < 0:
                lame2[i] = final[i][4] - final[i-1][4]
                lame2[i] = 0
                diffAffec.append(lame2[i])

            else:
                diffAffec.append(final[i][4] - final[i-1][4])

        return (diffAffec, diffDead)

    dA1, dD1 = calcDiff(pop1, beta1)
    dA2, dD2 = calcDiff(pop2, beta2)
    dA3, dD3 = calcDiff(pop3, beta3)

    # if code == 'BD':
    #     print(code, dA1, dA2, dA3)

    # ploting stuffs
    # init[:,0]-> dead, 1-> affected; change dA-> for dead
    prevVals = init[:, 1]
#     x = np.arange(datas, datas+360)
#     plt.plot(prevVals, color = 'b')
#     plt.plot(x,dA1, '--', color = 'r')
#     plt.plot(x,dA2, '--', color = 'black')
#     plt.plot(x,dA3, '--', color = 'r')
#     plt.title(f"{arr[0][0]}")
#     plt.show()
    # arr = np.flip(arr,0)

    # now lets create our report, which will be pushed into database
    name = arr[0][0]
    name = np.full((360, 1), name)
    code2 = arr[0][1]
    code2 = np.full((360, 1), code2)

    one_day = timedelta(days=1)
    yesterday_str = arr[-1][3]
    yesterday = dt.strptime(yesterday_str, '%Y-%m-%d').date()
    Today = np.full((360, 1), yesterday_str)

    day_predict = []
    for i in range(360):
        day = yesterday + one_day
        yesterday = day
        day = day.strftime("%Y-%m-%d")
        day_predict.append(day)
    day_predict = np.array(day_predict)
    day_predict = day_predict.reshape((360, 1))

    def createReport(string, v1, v2, v3):
        Type = np.full((360, 1), string)
        v1 = np.array(v1)
        v2 = np.array(v2)
        v3 = np.array(v3)
        v1 = v1.reshape((360, 1))
        v2 = v2.reshape((360, 1))
        v3 = v3.reshape((360, 1))
        values = np.hstack((Type, name, code2, Today, day_predict, v2, v1, v3))
        values = values.reshape((360, 8))
        return values

    reportAffec = createReport("Affected", dA1, dA2, dA3)
    reportDead = createReport("Dead", dD1, dD2, dD3)
    report = np.vstack((report[:idx, :], reportAffec,
                        reportDead, report[idx+720:, :]))
    idx = idx + 720

# report
# 0-> type (affected/ dead)
# 1-> country_name
# 2-> code2
# 3-> database pushing date
# 4-> prediction date
# 5-> middle val
# 6-> max val
# 7-> min val
# """

# #%%
# %%
noCountries = int(len(report)/720)
print(noCountries)

#print(len(report))

for k in range(len(report)):
    if report[k][1] == "Cote d'Ivoire":

        report[k][1] = "Cote dIvoire"

minCount = 0
maxCount = 0
count = 0
for k in range(len(report)):
    if(report[k][1] == "Peru"):
        count = count+1
        if(count == 1):
            minCount = k
        if (count == 720):
            maxCount = k


for k in range(720):
    report = np.delete(report, minCount, 0)     

noCountries = int(len(report)/720)
print(noCountries)
#%%



# max_value = np.max(report[:,7].astype(int))
# print(max_value)

# print(type(report[5][7]))

# print(max([int(r[7]) for r in report]))

# for i in range(0,len(report)):
#     if(int(report[i][7])==70428194495953802):
#         print(i,report[i][1])
    
    


with open("data.sql", "w") as sql_file:
    for j in range(len(report)):
        sql_file.write("INSERT INTO longtermprediction(region_id,alpha2,type,insertion_date,prediction_date,median,maximum,minimum,name)VALUES((select id from regions where alpha2 = '%s'LIMIT 1),'%s','%s','%s','%s',%s,%s,%s,'%s');\n" % (
            report[j][2], report[j][2], report[j][0], report[j][3], report[j][4], report[j][5], report[j][6], report[j][7], report[j][1]))


sql_file = open("data.sql", "r")

count2 = 0

try:
    connection = psycopg2.connect(
        "dbname='postgres' user='admin_corona@corona-forecast' host='corona-forecast.postgres.database.azure.com' port='5432' password='T0wardsResolution'")
    cursor = connection.cursor()

    # Print PostgreSQL Connection properties
    print(connection.get_dsn_parameters(), "\n")

    # Print PostgreSQL version
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to - ", record, "\n")

    cursor.execute(sql_file.read())

    connection.commit()
    count = cursor.rowcount
    count2= count2+1
    print(count2)
    print(count, "Record inserted successfully into worldprediction table")

except (Exception, psycopg2.Error) as error:
    if(connection):
        print("Failed to insert record into worldprediction table", error)

finally:
    # closing database connection.
    if(connection):
        cursor.close()
        connection.close()
    print("PostgreSQL connection is closed")
