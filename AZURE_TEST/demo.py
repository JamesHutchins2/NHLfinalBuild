import textwrap
import pypyodbc as odbc
import pandas as pd 

###############################################################
#specify driver 
driver = '{ODBC Driver 18 for SQL Server}'
#specify server name
server_name = 'western-ai'
#specify database name
database = 'NHLData'

#server string 

server = '{server_name}.database.windows.net,1433'.format(server_name=server_name)

#define user and passoword


connection_string = textwrap.dedent('''
    Driver={driver};
    Server={server};
    Database={database};
    Uid={username};
    Pwd={password};
    Encrypt=yes;
    TrustServerCertificate=no;
    Connection Timeout=30;
    '''.format(
        driver=driver, 
        server=server, 
        database=database, 
        username=username, 
        password=password 
))


#create new PYODBC connection
cnxn: odbc.Connection = odbc.connect(connection_string)

#create cursor
cursor: odbc.Cursor = cnxn.cursor()
print('Connection Successful')
cnxn.close()