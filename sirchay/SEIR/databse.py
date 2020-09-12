## function for Select query

def getRegion(regID):
    try:
        

       
    # Print PostgreSQL Connection properties
        print ( connection.get_dsn_parameters(),"\n")

    # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record,"\n")
    
        postgres_select_query = "select id from regions where alpha2 = %s"
       
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


## function for  Insert query

def insertInfo2(regid,alpha2,typ,ins_date,pred_date,median,maxi,mini,name):
    try:
        postgres_insert_query = """INSERT INTO longtermprediction(region_id,alpha2,type,insertion_date,prediction_date,median,maximum,minimum,name)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        cursor.execute(postgres_insert_query, (regid,alpha2,typ,ins_date,pred_date,median,maxi,mini,name))

        connection.commit()
        count = cursor.rowcount
        print (count, "Record inserted successfully into countryprediction table")
        
    except (Exception, psycopg2.Error) as error :
        if(connection):
            print("Error inserting data in PostgreSQL table", error)


## pushing

import psycopg2
connection = psycopg2.connect(user = "teamcoronosis",
                                  password = "p1jGQwEMANAGZ5b72xWh",
                                  host = "coronosis.cfzyz28p01p7.ap-south-1.rds.amazonaws.com",
                                  port = "5432",
                                  database = "postgres")
cursor = connection.cursor()

#selecting regionIds


        
    #finally:
    #closing database connection.
#inserting into countryprediction table     



#calling functions

regid=[]

for i in range(len(report)):
    regid=getRegion(report[i][2])
    insertInfo2(regid,report[i][2],report[i][0],report[i][3],report[i][4],report[i][5],report[i][6],report[i][7],report[i][1])
    print(i)

#closing connection
if(connection):
    cursor.close()
    connection.close()
    print("PostgreSQL connection is closed")



## Alternative: Making a sql script file and reading this


with open("1.sql","w") as sql_file:
    for j in range(len(report)):
        sql_file.write("INSERT INTO longtermprediction(region_id,alpha2,type,insertion_date,prediction_date,median,maximum,minimum,name)VALUES((select id from regions where alpha2 = '%s'LIMIT 1),'%s','%s','%s','%s',%s,%s,%s,'%s');\n" % (report[j][2],report[j][2],report[j][0],report[j][3],report[j][4],report[j][5],report[j][6],report[j][7],report[j][1]))
        
connection = psycopg2.connect(user = "teamcoronosis",
                                  password = "p1jGQwEMANAGZ5b72xWh",
                                  host = "coronosis.cfzyz28p01p7.ap-south-1.rds.amazonaws.com",
                                  port = "5432",
                                  database = "postgres")
cursor = connection.cursor()

cursor.execute(open("1.sql", "r").read())

if(connection):
    cursor.close()
    connection.close()
    print("PostgreSQL connection is closed")



## function for Delete query

def deleteData(date):
    try:
        connection = psycopg2.connect(user = "teamcoronosis",
                                  password = "p1jGQwEMANAGZ5b72xWh",
                                  host = "coronosis.cfzyz28p01p7.ap-south-1.rds.amazonaws.com",
                                  port = "5432",
                                  database = "postgres")
        cursor = connection.cursor()

        # Update single record now
        sql_delete_query = """Delete from longtermprediction where insertion_date = %s"""
        cursor.execute(sql_delete_query, (date, ))
        connection.commit()
        count = cursor.rowcount
        print(count, "Record deleted successfully ")

    except (Exception, psycopg2.Error) as error:
        print("Error in Delete operation", error)

    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


## calling function
deleteData('2020/06/16')

## selecting all rows

connection = psycopg2.connect(user = "teamcoronosis",
                                  password = "p1jGQwEMANAGZ5b72xWh",
                                  host = "coronosis.cfzyz28p01p7.ap-south-1.rds.amazonaws.com",
                                  port = "5432",
                                  database = "postgres")
cursor = connection.cursor()
cursor.execute("select * from longtermprediction")
reg = cursor.fetchall()
for r in reg:
    print(r)
if(connection):
    cursor.close()
    connection.close()
    print("PostgreSQL connection is closed")


