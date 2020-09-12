#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 01:19:29 2020

@author: hisham
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 21:31:02 2020

@author: hisham
"""

# import math
import chardet
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


import requests
import json
from flask import jsonify
from csv import writer


"""
url = 'https://corona-api.com/countries/'
url_iso2 = 'https://restcountries.eu/rest/v2/'

querystring = {"country":"Bangladesh"}

headers = {
    'x-rapidapi-host': "coronavirus-monitor.p.rapidapi.com",
    'x-rapidapi-key': "b23312c441msh260b60b1bd6e484p1f47f7jsnd56b11696dd9"
    }

response_iso2 = requests.get(url_iso2)


lst_iso2 = json.loads(response_iso2.text)

# for i in lst_iso2:
#     print(i['alpha2Code'])

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
        print(lnk)
        response = requests.get(lnk)
    

        lst = json.loads(response.text)
        print(country_name)
        if 'data' in lst:
            if(len(lst['data']['timeline']) > 0):
                for j in lst['data']['timeline']:
                    date = j['date']
                    new_confirmed = j['new_confirmed']
                    new_deaths = j['new_deaths']
                    entry = [country_name, country_code2, country_code3, date, new_confirmed, new_deaths]
                    csv_writer.writerow(entry)
"""

                    
with open('country_timeline1.csv', 'rb') as f:
    result = chardet.detect(f.read())  # or readline if the file is large

dataset = pd.read_csv('country_timeline1.csv', keep_default_na=False,  encoding=result['encoding'])
X = dataset.iloc[:, :].values
Z = dataset.iloc[0:540, :].values


def buildZ(i, date):
    for row in X:
        if row[3] == date:
            # print(row)
            Z[i] = row
            i = i + 1
    print(i)            
    return i
i = 0
index = buildZ(i, '2020-04-19')
index = buildZ(index, '2020-04-18')
index = buildZ(i+index, '2020-04-17')

for i in range(180):
    if (Z[i][0] != Z[i+180][0]) or (Z[i][0] != Z[i+360][0]):
        print(Z[i][0])
        
top = Z
top = np.append(top, np.zeros((540,8)), axis = 1)

for i in range(180):
    top[i][6] = top[i+180][4]
    top[i][7] = top[i+180][5]
    top[i][8] = top[i+2*180][4]
    top[i][9] = top[i+2*180][5]

""" here we go for polynomial"""
"""
countries = Z[0:180, 0]
# country = "Iran (Islamic Republic of)"
cidx = 0
for country in countries:
    i = 0
    for row in X:
        if row[0] == country and (row[3] != "2020-04-20" and row[3] != "2020-04-19"): 
            i = i+ 1
    print(i)
    
    arr = np.empty((i, 6), dtype=object)
    
    i = 0
    for row in X:
        if row[0] == country and row[3] != "2020-04-20" and row[3] != "2020-04-19": 
            arr[i]=row
            i = i + 1
    print(i)
     
    arr = arr[np.argsort(arr[:,3])]
    
    val = np.arange(i)
    val = val.reshape((len(val),1))
    
    X_train, y_train = val, arr[:,5]
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.linear_model import LinearRegression
    poly_reg = PolynomialFeatures(degree = 6)
    X_poly = poly_reg.fit_transform(X_train)
    poly_reg.fit(X_poly, y_train) 
    lin_reg_2 = LinearRegression()
    lin_reg_2.fit(X_poly, y_train)
    
    # Visualising the Polynomial Regression results
    # plt.scatter(ZX, Z1)
    plt.scatter(X_train, y_train)
    y_pred = lin_reg_2.predict(X_poly)
    X_train = np.sort(X_train, axis = 0)
    y_pred = np.sort(y_pred, axis = 0)
    # print (X_train)
    plt.plot(X_train, y_pred, color = 'r')
    # plt.plot(X_train, lin_reg_2.predict(X_poly), color = 'red')
    plt.title('Death rate analysis')
    plt.ylabel('% of deaths in closed case')
    plt.xlabel('date')
    plt.show()
    print(country)
    
    temp=np.array([i])
    temp=temp.reshape(len(temp),1)
    # print(lin_reg_2.predict(poly_reg.fit_transform(temp)))
    ans = lin_reg_2.predict(poly_reg.fit_transform(temp))
    if ans < 0: 
        top[cidx][11] = 0
    else:
        top[cidx][11] = ans
    cidx = cidx + 1
    # print(country)
"""  

def inputTop(d, a, b, c):
    for i in range(len(top)):
        avg = (top[i][a] + top[i][b] + top[i][c])/3
        
        if top[i][a] > top[i][b] and top[i][b] > top[i][c]:
            if avg/top[i][a] < 1.15:
                top[i][d] = avg + (top[i][a] - top[i][c])/4 - (top[i][a] - top[i][b])/2
            else:
                top[i][d] = avg + (top[i][a] - top[i][c])/4 - (top[i][a] - top[i][b])/3
            # print(top[i][0])
            if top[i][d] < 0:
                top[i][d] = 0            
        elif top[i][a] < top[i][b] and top[i][b] < top[i][c]:   
            if (avg/top[i][b]) < 0.75:
                top[i][d] = avg - (top[i][b] - top[i][a])/2 + (top[i][c] - top[i][b])/2
            elif (avg/top[i][b]) > 1.30:
                top[i][d] = avg - (top[i][c] - top[i][b])/2 + (top[i][b] - top[i][a])/2
            else:
                top[i][d] = avg - (top[i][c] - top[i][a])/3 + (top[i][c] - top[i][b])/5     
            if top[i][d] < 0:
                top[i][d] = 0
        else:
            if top[i][a] > top[i][b] and top[i][b] < top[i][c]:
                # print(top[i][0])
                top[i][d] = avg + (top[i][a] - top[i][b])/6
            elif top[i][a] < top[i][b] and top[i][b] > top[i][c]:              
                top[i][d] = avg + (top[i][b] - top[i][a])/6
            else:
                top[i][d] = avg
                
inputTop(10, 4, 6, 8)
inputTop(11, 5, 7, 9)
inputTop(12, 10, 4, 6)
inputTop(13, 11, 5, 7)
top[:, [10,11,12,13]] = top[:, [10,11,12,13]].astype(int)

dbase = top[0:180, [0, 2, 3, 4, 5, 10, 11, 12, 13]]

# date manipulation
from datetime import datetime as dt, timedelta
one_day = timedelta(days=1)
yesterday_str = dbase[0][2]
yesterday = dt.strptime(yesterday_str, '%Y-%m-%d').date()
today = yesterday + one_day
today_str = today.strftime("%Y-%m-%d")
i = np.full((180,1), today_str)
dbase = np.hstack((dbase[:,:5], i, dbase[:,5:]))
tomorrow = today + one_day
tomorrow_str = tomorrow.strftime("%Y-%m-%d")
i = np.full((180,1), tomorrow_str)
dbase = np.hstack((dbase[:,:8], i, dbase[:,8:]))


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

# np.savetxt("country.txt", top[0:180, 0], fmt="%s", newline="\",\"")
# np.savetxt("d-1A.txt", top[0:180, 4], fmt="%s", newline=",")
# np.savetxt("d-1D.txt", top[0:180, 5], fmt="%s", newline=",")
# np.savetxt("dA.txt", top[0:180, 10], fmt="%s", newline=",")
# np.savetxt("dD.txt", top[0:180, 11], fmt="%s", newline=",")
# np.savetxt("d+1A.txt", top[0:180, 12], fmt="%s", newline=",")
# np.savetxt("d+1D.txt", top[0:180, 13], fmt="%s", newline=",")

