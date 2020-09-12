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


import psycopg2
connection = psycopg2.connect(user = "teamcoronosis",
                                  password = "p1jGQwEMANAGZ5b72xWh",
                                  host = "coronosis.cfzyz28p01p7.ap-south-1.rds.amazonaws.com",
                                  port = "5432",
                                  database = "postgres")
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
    