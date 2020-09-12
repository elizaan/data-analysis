import requests
import json
from flask import jsonify
from csv import writer
import numpy as np

url = 'https://corona-api.com/countries/'
url_iso2 = 'https://restcountries.eu/rest/v2/'

querystring = {"country":"Bangladesh"}

headers = {
    'x-rapidapi-host': "coronavirus-monitor.p.rapidapi.com",
    'x-rapidapi-key': "b23312c441msh260b60b1bd6e484p1f47f7jsnd56b11696dd9"
    }

# response = requests.get(url)
response_iso2 = requests.get(url_iso2)
# print(type(json.loads(response.text)['stat_by_country']))
# c = 0
# for i in response:
#     obj = i.decode("utf-8")
#     print(obj)
#     # print(json.loads(obj)['country'])
#     c += 1
#     if c > 2:
#         break

# print(response.text)


# lst = json.loads(response.text)
# print(lst['data']['timeline'][0]['date'])
# print(lst['data']['timeline'][0]['new_confirmed'])
# print(lst['data']['timeline'][0]['new_deaths'])

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
        # print(lst)


        # print(lst['data']['timeline'][0]['date'])
        # print(lst['data']['timeline'][0]['new_confirmed'])
        # print(lst['data']['timeline'][0]['new_deaths'])



# for i in range(0,10):
#     print(lst[i])


# with open('bd_corona.csv', 'w') as csv_file:
#     csv_writer = writer(csv_file)
#     headers = ['Date', 'Total Cases', 'Total Cured', 'Total Death', 'Newly Affected']
#     csv_writer.writerow(headers)
#     c = 0
#     for i in lst:
#         if c < 7:
#             c += 1
#             continue
#         rd = i['record_date']
#         tc = i['total_cases']
#         tr = i['total_recovered']
#         td = i['total_deaths']
#         nc = i['new_cases']
#         entry = np.array([rd, tc, tr, td, nc])
#         entry = np.where(entry=="", 0, entry)
        
#         csv_writer.writerow(entry)
#         c = 0







# import requests

# url = "https://covid-193.p.rapidapi.com/statistics"

# headers = {
#     'x-rapidapi-host': "covid-193.p.rapidapi.com",
#     'x-rapidapi-key': "b23312c441msh260b60b1bd6e484p1f47f7jsnd56b11696dd9"
#     }

# response = requests.request("GET", url, headers=headers)

# print(response.text)