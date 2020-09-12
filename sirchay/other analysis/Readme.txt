1. temperature correlation :
    folder : Temperature + humidity
    code : Affected + temprature.ipynb
    input:weather_data_countries_covid19.csv, country_model_e.csv, temperaturehumidity.csv,temperaturehumidity2.csv
    output : temperaturelatonfindings.csv (just wrote whether correlated or not : no other tags have been used, median added)
    
2. humidity correlation :
    folder : Temperature + humidity
    code : Affected+ humidity.ipynb
    input:weather_data_countries_covid19.csv, country_model_e.csv, temperaturehumidity.csv, temperaturehumidity2.csv
    output: humidityrelatonfindings.csv (just wrote whether correlated or not : no other tags have been used, median added)
    
3. scatter plot of food security vs afftected 
    folder: foodsecurity
    code : foodsecurity.ipynb
    input: countrylatestactive.csv, countrylatestactive2.csv, global_food_index_ranking_comma.csv
    output: affected+food.csv (just covid data and food security data are merged together so that we can make a table in latex just importing it)
    
4. scatter plot of pollution vs afftected 
    folder: pollution
    code : pollutionindex.ipynb
    input: countrylatestactive.csv, countrylatestactive2.csv, global_pollution_index_ranking_comma.csv
    output: affected+pollution.csv (just covid data and pollution index data are merged together so that we can make a table in latex just importing it)


5. scatter plot of heallthcare vs recovered 
    folder: healthcare
    code : healthcareindex.ipynb
    input: countrylatestactive.csv, countrylatestactive2.csv, global_health_index_ranking_comma.csv
    output: recovered+health.csv (just covid data and pollution index data are merged together so that we can make a table in latex just importing it)

6. scatter plot of tests vs deathrate 
    folder: populationtest
    code : population test.ipynb
    input: country_populationtests.csv
    output: deathrate+tests.csv (just covid data and pollution index data are merged together so that we can make a table in latex just importing it)
    
screenshots are added in folders