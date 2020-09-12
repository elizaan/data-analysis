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
import psycopg2
import csv


import requests
import json
from flask import jsonify
from csv import writer


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
        print(country_code2)
        if 'data' in lst:
            if(len(lst['data']['timeline']) > 0):
                for j in lst['data']['timeline']:
                    date = j['date']
                    new_confirmed = j['new_confirmed']
                    new_deaths = j['new_deaths']
                    entry = [country_name, country_code2, country_code3, date, new_confirmed, new_deaths]
                    csv_writer.writerow(entry)


#insert 18th april's actual values first , I haven't run it yet. so i don't know it will work or not

csv_input1 = pd.read_csv('PredOutput.csv')
csv_input2 = pd.read_csv('country_timeline1.csv')
for line1 in csv_input1:
    for line2 in csv_input2:
        if line2['Date'] == line1['date'] and line2['Country_name'] == line1['country_name']
            csv_input1['actual_affected'] = csv_input2['New_confirmed']
            csv_input1['actual_death'] = csv_input2['New_death']


csv_input1.to_csv('PredOutput.csv', index=False)

#Maybe you have to right a function to new append values on the actual affected and death column .my code may be have bugs as I couldn't run to insert actual values.Google koren :(

#your prediction code                  
with open('country_timeline1.csv', 'rb') as f:
    result = chardet.detect(f.read())  # or readline if the file is large

dataset = pd.read_csv('country_timeline1.csv', keep_default_na=False,  encoding=result['encoding'])
X = dataset.iloc[:, :].values
Z = dataset.iloc[0:540, :].values


def buildZ(i, date):
    for row in X:
        if row[3] == date:
            Z[i] = row
            i = i + 1
    # print(i)            
i = 0
buildZ(i, '2020-04-16')
buildZ(i+180, '2020-04-15')
buildZ(i+2*180, '2020-04-14')


for i in range(180):
    if (Z[i][0] != Z[i+180][0]) or (Z[i][0] != Z[i+360][0]):
        print(Z[i][0])
        
new = Z
new = np.append(new, np.zeros((540,8)), axis = 1)

for i in range(180):
    new[i][6] = new[i+180][4]
    new[i][7] = new[i+180][5]
    new[i][8] = new[i+2*180][4]
    new[i][9] = new[i+2*180][5]

top = new

def inputTop(d, a, b, c):
    for i in range(len(top)):
        avg = (top[i][a] + top[i][b] + top[i][c])/3
        
        if top[i][a] > top[i][b] and top[i][b] > top[i][c]:
            top[i][d] = top[i][a] + (top[i][a] - top[i][c])/4 - (top[i][b] - top[i][c])/4
            if top[i][d] < 0:
                top[i][d] = 0            
        elif top[i][a] < top[i][b] and top[i][b] < top[i][c]:   
            top[i][d] = avg - (top[i][c] - top[i][a])/4 + (top[i][c] - top[i][b])/3 
            if top[i][d] < 0:
                top[i][d] = 0
        else:
            if top[i][a] > top[i][b] and top[i][b] < top[i][c]:
                top[i][d] = avg + (top[i][a] - top[i][b])/5
            elif top[i][a] < top[i][b] and top[i][b] > top[i][c]:              
                top[i][d] = avg + (top[i][b] - top[i][c])/5
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


#connection started

connection = psycopg2.connect(user = "zbmdacuv",
                                  password = "IesK82sq2gGKuzffnFdcl3kqcKs5-irT",
                                  host = "arjuna.db.elephantsql.com",
                                  port = "5432",
                                  database = "zbmdacuv")
cursor = connection.cursor()

#selecting regionIds

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

       # connection.commit()
       # count = cursor.rowcount
       # print (count, "Record inserted successfully into worldprediction table")

    except (Exception, psycopg2.Error) as error :
        if(connection):
            print("Error fetching data from PostgreSQL table", error)
        
    #finally:
    #closing database connection.
#inserting into countryprediction table     
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


#calling functions

regid=[]
for i in range(180):
    regid=getRegion(dbase[i][1])
    insertInfo(regid,dbase[i][1],dbase[i][0],dbase[i][2],dbase[i][3],dbase[i][4],dbase[i][6],dbase[i][7],dbase[i][9],dbase[i][10],0)
    print(i)

#closing connection
if(connection):
    cursor.close()
    connection.close()
    print("PostgreSQL connection is closed")


#checking thikmoto insert hoise kina 

try:
    
    connection = psycopg2.connect(user = "zbmdacuv",
                                  password = "IesK82sq2gGKuzffnFdcl3kqcKs5-irT",
                                  host = "arjuna.db.elephantsql.com",
                                  port = "5432",
                                  database = "zbmdacuv")
    cursor = connection.cursor()
    postgres_select_query2 = "select affected_1 from countryprediction where country_name = %s"
    rec = 'Bangladesh'
    cursor.execute(postgres_select_query2,(rec,) )
    shoytan = cursor.fetchall()
    for r in shoytan :
        print(r[0])

except (Exception, psycopg2.Error) as error :
        if(connection):
            print("Error fetching data from PostgreSQL table", error)
finally:
    if(connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
		
		
		
		
#inserted 18th april data to PredOutput.csv file

""""import csv

with open("PredOutput.csv", "w") as f2:
    fieldnames = ['country_name','date','affected_prediction','death_prediction']
    csv_writer = csv.DictWriter(f2, fieldnames= fieldnames)
    csv_writer.writeheader()
    csv_writer = csv.writer(f2)
    csv_writer.writerows(tempbase)"""
	
#you have to just call the below function to append later date's data

import csv

def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)
        
append_list_as_row('PredOutput.csv',tempbase)	