#!/usr/bin/env python
# coding: utf-8

# In[9]:


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 17:18:07 2020

@author: hisham
"""


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
import math
from datetime import datetime as dt, timedelta
# import plotly.graph_objects as go
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
    if X[i][3] == t and X[i][4] >= 40:
        codeList.append(X[i][1])
    i = i + 1
# print(len(codeList) == len(set(codeList)))
codeIndex = 1
report = np.empty((0, 8), object)
idx = 0


code = 'IN'

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
            arr[datas]=row
            datas = datas+ 1
    print(arr[0][0])
    
    
    arr = arr[np.argsort(arr[:,3])]
    # init: previous values (0 for dead, 1 for affected)
    init = np.empty((datas, 2), dtype= object)
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
            if arr[i][3] >= "2020-03-05":   
                if l<0:
                    l=0  #timing considered from March 05 to see its growing shape
                lst.append(l)
        return lst
    
    """"lamdaD = calLamda(True)
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
    maxConst = 1000
    midConst = 300
    pop1 = pop / minConst
    beta1 = (lbsl / pop1)
    
    pop3 = pop / maxConst
    beta3 = (lbsl / pop3)
    
    pop2 = pop / midConst
    beta2 = (lbsl / pop2)"""
    
    ##hishu hospital theke dise
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
            l = (fplus - splus)/ splus    
        if arr[i][3] >= "2020-03-05":                           #timing considered from March 05 to see its growing shape
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
    maxconst = 800
    midconst = 175
    minconst = 80
    pop1 = pop / minconst
    beta1 = (lbsl / pop1)
    pop3 = pop / maxconst
    beta3 = (lbsl / pop3)
    pop2 = pop / midconst
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
            if final[i][0]> sys.maxsize or final[i][1]> sys.maxsize or final[i][2]> sys.maxsize or final[i][3]> sys.maxsize :
                final[i][0]=0
                final[i][1]=0
                final[i][2]=0
                final[i][3]=0
            if np.isnan(final[i][0]) or np.isnan(final[i][1]) or np.isnan(final[i][2]) or np.isnan(final[i][3]) or math.isinf(final[i][0]) or math.isinf(final[i][1]) or math.isinf(final[i][2]) or math.isinf(final[i][3]):
                final[i][0]=0
                final[i][1]=0
                final[i][2]=0
                final[i][3]=0
            
            
        final[:, [0,1,2,3]] = final[:, [0,1,2,3]].astype('int64')    
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
print("length of report and codelist")
print(len(report)/60) 
print(len(codeList))

names = []

for i in range(len(X)):
    for j in range(len(codeList)):
        if codeList[j] == X[i][1]:
            dbase[j][0] = X[i][0]
            dbase[j][1] = X[i][2]
            dbase[j][2] = t
            if X[i][3] == t:
                dbase[j][3] = X[i][4] - X[i+1][4]
                dbase[j][4] = X[i][5] - X[i+1][5]
        j = j+1
    i = i+1
# j = 0
# i = country_data-1
# for j in range(noCountries):
#     # print(i)
# #     if X[i][0] == "Serbia" or X[i][0] == "Antigua and Barbuda":
# #         del X[i][0]
# #         del X[i][2] 
# #         del X[i][3]
# #         del X[i][4]
# #         del X[i][5] 
        
# #         X[i][0] = X[i+1][0]
# #         X[i][2] = X[i+1][2]
# #         X[i][3] = X[i+1][3]
# #         X[i][4] = X[i+1][4]
# #         X[i][5] = X[i+1][5]
        
#     dbase[j][0] = X[i][0]
#     dbase[j][1] = X[i][2]
#     dbase[j][2] = t
#     dbase[j][3] = X[i][4] - X[i-1][4]
#     dbase[j][4] = X[i][5] - X[i-1][5]
#     j = j+1
#     i = i + country_data
    
i = 0
for j in range(noCountries):
    dbase[j][5] = report[i][4]
    dbase[j][6] = report[i][4+2]
    dbase[j][7] = report[i+30][4+2]
    dbase[j][8] = report[i+1][4]
    dbase[j][9] = report[i+1][4+2]
    dbase[j][10] = report[i+30+1][4+2]
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

#%%
def getRegion(regID):
    try:
        

       
    # Print PostgreSQL Connection properties
        print ( connection.get_dsn_parameters(),"\n")

    # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record,"\n")
    
        postgres_select_query = "select id from regions where alpha3 = %s"
       
        cursor.execute(postgres_select_query, (regID,))
        
        reg = cursor.fetchall()
        for r in reg :
            print(r[0])
            return r[0]
        #print(reg)

       # connection.commit()
       # count = cursor.rowcount
       # print (count, "Record inserted successfully into worldprediction table")

    except (Exception, psycopg2.Error) as error :
        if(connection):
            print("Error fetching data from PostgreSQL table", error)
    
    #return reg[0]
    


# In[11]:


def insertInfo(regid,alpha3,name,date,affected_1,death_1,affected_2,death_2,affected_3,death_3,pred):
    try:
        postgres_insert_query = """INSERT INTO countryprediction(region_id,alpha_3,country_name, date , affected_1, death_1 , affected_2, death_2 , affected_3, death_3 , prediction_calculation)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        cursor.execute(postgres_insert_query, (regid,alpha3,name,date,affected_1,death_1,affected_2,death_2,affected_3,death_3,pred))

        connection.commit()
        count = cursor.rowcount
        print (count, "Record inserted successfully into countryprediction table")
        
    except (Exception, psycopg2.Error) as error :
        if(connection):
            print("Error inserting data in PostgreSQL table", error)

    


# In[12]:


connection = psycopg2.connect("dbname='postgres' user='admin_corona@corona-forecast' host='corona-forecast.postgres.database.azure.com' port='5432' password='T0wardsResolution'")
cursor = connection.cursor()

regid=[]
for i in range(tot_countries):
    regid=getRegion(dbase[i][1])
    insertInfo(regid,dbase[i][1],dbase[i][0],dbase[i][2],dbase[i][3],dbase[i][4],dbase[i][6],dbase[i][7],dbase[i][9],dbase[i][10],0)
    print(i)

#closing connection
if(connection):
    cursor.close()
    connection.close()
    print("PostgreSQL connection is closed")


# In[15]:


# import matplotlib.pyplot as plt
# import datetime
# from matplotlib.ticker import MultipleLocator
# import numpy as np
# import pandas as pd
# # from readdb import readb
# import psycopg2 as pg
# # import consts
# # print(consts.avar)
# # connection = pg.connect("dbname='postgres' user='teamcoronosis' host='coronosis.cfzyz28p01p7.ap-south-1.rds.amazonaws.com' port='5432' password='p1jGQwEMANAGZ5b72xWh'")
# connection = pg.connect("dbname='postgres' user='admin_corona@corona-forecast' host='corona-forecast.postgres.database.azure.com' port='5432' password='T0wardsResolution'")
# for i in range(len(consts.avar)):
#     plt.rcParams["font.family"] = "Times New Roman"
#     plt.xticks(rotation=30,fontsize=20)
#     plt.yticks(fontsize=20)
#     # plt.gcf().set_size_inches(8.27, 4.25)
#     # dateparsef = lambda x: datetime.strptime(str(x), "%Y-%m-%d")
#     dateparsef = lambda x: x

#     # data = pd.read_csv('ar_aff.csv',parse_dates = ['date'],date_parser = dateparsef)
#     # data = pd.read_excel('activerate.xlsx',sheet_name='Sheet15',parse_dates = ['date'],date_parser = dateparsef)
#     # data = pd.read_excel('activerate.xlsx',sheet_name='Sheet19',parse_dates = ['date'])
#     var_1 = consts.avar[i][1]
#     var_2 = consts.avar[i][2]
#     data = readb(var_1,var_2,connection)
#     # cond = data['date'] >= datetime.date(2020, 8, 2)
#     # data = data[cond]
#     plt.plot(data.date,data.Global,label = 'Global',linestyle='-',linewidth=2.5)
#     plt.plot(data.date,data.USA,label = 'USA',linestyle='--',linewidth=2.5)
#     plt.plot(data.date,data.Russia,label = 'Russia',linestyle='-.',linewidth=2.5)
#     plt.plot(data.date,data.Bangladesh,label = 'Bangladesh',linestyle=':',linewidth=2.5)
#     plt.plot(data.date,data.Indoneshia,label = 'Indoneshia',dashes=[3, 3, 1, 3],linewidth=2.5)
#     plt.plot(data.date,data['United Kingdom'],label = 'United Kingdom',dashes=[2,2,5,2],linewidth=2.5)
#     plt.plot(data.date,data.India,label = 'India',dashes=[1,3,5,4],linewidth=2.5)
#     plt.plot(data.date,data.Italy,label = 'Italy',dashes=[1,3,1,3,5,4],linewidth=2.5)
#     plt.plot(data.date,data.Spain,label = 'Spain',dashes=[1,3,4,3,5,4],linewidth=2.5)
#     plt.plot(data.date,data.China,label = 'China',dashes=[1,3,1,3,4,2,5,4],linewidth=2.5)
#     plt.plot(data.date,data.Brazil,label = 'Brazil',dashes=[1,3,1,3,1,1,5,4],linewidth=2.5)
#     #      area/100km^2
#     #      populaton/million
#     #      affected
#     #      recovered
#     plt.ylabel(consts.avar[i][3],fontsize=25)
#     # Set the y axis label of the current axis.
#     plt.xlabel('Date',fontsize=25)
#     plt.subplots_adjust(left=0.08, bottom=0.16, right=.97, top=.95, wspace=.2, hspace=.2)
#     # Set a title of the current axes.
#     # plt.title('')
#     # show a legend on the plot
#     # plt.legend(bbox_to_anchor=(1.1, 1.05))
#     # plt.legend(ncol=2,fontsize=17)

#     # plt.legend(fontsize=17,loc='lower left')
#     plt.legend(fontsize=17)
#     # spacing = 10
#     # minorLocator = MultipleLocator(spacing)
#     # plt.gca().yaxis.set_minor_locator(minorLocator)
#     spacing = 7
#     minorLocator = MultipleLocator(spacing)
#     # plt.gca().xaxis.set_minor_locator(minorLocator)
#     plt.gca().xaxis.set_major_locator(minorLocator)
#     plt.grid(dashes=[1,3],color='black',linewidth=.75)
#     # plt.grid(linestyle='-',color='black',which='major')
#     # Display a figure.
#     # plt.savefig(fname='a.pdf',format='pdf')
#     # manager = plt.get_current_fig_manager()
#     # manager.frame.Maximize(True)
#     # manager.resize(*manager.window.maxsize())
#     # manager.window.showMaximized()
#     # plt.show()
#     fig = plt.gcf()
#     fig.set_size_inches(18.5, 10.5)
#     plt.savefig(f'{consts.avar[i][0]}.svg',papertype='a4')
#     data.to_html(f'{consts.avar[i][0]}.html')


# In[ ]:




