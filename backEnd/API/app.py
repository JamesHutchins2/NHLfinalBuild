import os 
from flask import Flask, request
from flask_cors import CORS
from datetime import datetime, timezone
import psycopg2
import joblib
import textwrap
import pypyodbc as odbc
import pandas as pd 
#import chatbot code 

import sys
sys.path.insert(1, 'D:/NHLProject/backEnd/ChatBot')
from bot_wrapper import BotWrapper

#specify driver 
driver = '{ODBC Driver 18 for SQL Server}'

#specify server name
server_name = 'western-ai'

#specify database name
database = 'NHLData'

#server string 
server = '{server_name}.database.windows.net,1433'.format(server_name=server_name)

#define user and passoword
username = ''
password = ''

#create connection object 
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
#import model
clf = joblib.load('svm_model.pkl')

# ! lets define the data base query set
# ? stats (data set)
CREATE_STATS_TABLE  = ("""IF OBJECT_ID('stats', 'U') IS NULL
BEGIN
    CREATE TABLE stats (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(100),
        age INT,
        Tm NVARCHAR(100),
        Pos NVARCHAR(100),
        GP INT,
        G INT,
        A INT,
        PTS INT,
        PLUS_MINUS INT,
        PIM INT,
        year INT
        );
END;
""")

# ! this is a table we could potenrially populate with prospects
CREATE_PLAYERS_MODEL_TABLE = """IF OBJECT_ID('players', 'U') IS NULL
BEGIN
    CREATE TABLE players (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(100),
        games_played INT,
        goals INT,
        penalty_minutes FLOAT,
        position_D INT,
        position_LW INT,
        model_result FLOAT
    );
END;"""

# * insertes players into the players table
INSERT_PLAYER = """INSERT INTO players (name, games_played, goals, penalty_minutes, position_D, position_LW, model_result) VALUES (?,?,?,?,?,?,?)"""

# * finds a player by name
FIND_PLAYER_byName = "SELECT * FROM players WHERE name=%s;"
# * finds a player by id
FIND_PLAYER_byID = "SELECT * FROM players WHERE id=%s;"


# ! querys to search stats data base by name and year (this will be used to get the stats for the player)





#initialize flask app
app = Flask(__name__)
CORS(app)
#create connection to azure database
connection: odbc.Connection = odbc.connect(connection_string)


# ! ################################### #############

# ? player (model data set) find player by name
@app.post("/api/player")
def get_player():
    name = request.get_json()["name"]
    #query the database for the player
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM players WHERE name=%s", (name,))
    player = cursor.fetchone()
    cursor.close()

    if(player == None):
        return{"message": "player not found"}
    else:
        return {"player": player}


#method to add players to the database 

@app.post("/data/addPlayers")
def add_players():
    data = request.get_json()
    cursor = connection.cursor()
    #create table if it does not exist
    cursor.execute(CREATE_PLAYERS_MODEL_TABLE)
    cursor.execute(INSERT_PLAYER, (data["name"], data["games_played"], data["goals"], data["penalty_minutes"], data["position_D"], data["position_LW"], data["model_result"]))
    connection.commit()
    cursor.close()
    return {"message": "player added successfully."}

#method for getting all players
@app.get("/api/allplayers")
def get_all_players():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM players")
    players = cursor.fetchall()
    cursor.close()
    return {"players": players}

# ! ################################################
import re 
# ! ################################################
#import nltk
import nltk.tokenize as tk
def player_search_call(user_input):
    #parse user input to find player name
    year = re.search(r'\d{4}', user_input).group()
    print(year)
    #query the db for each value until a response if given (name)
    #we will be searching by name and year
    player = None
    words = tk.word_tokenize(user_input)
    for word in words:
        print(word)
        
        player = get_player_stats(name=word, year=year)
        if(player != None):
            for i in range(0,11):
                print(player[i])
            return {
                        "name": player[1],
                        "Age": int(player[2]),
                        "G": int(player[5]),
                        "Tm":   player[3],
                        "Pos": player[4],
                        "GP": player[6],
                        "A": player[7],
                        "PTS": player[8],
                        "plusMinus": int(player[9]),
                        "PIM": int(player[10]),
                        "year": int(player[11])

                    }
    return None

    





   
# ? stats (data set) add player to stats table 
@app.post("/api/stats/insert")
def insert_stats():
    data = request.get_json()
    cursor = connection.cursor()
    #create table if it does not exist
    cursor.execute(CREATE_STATS_TABLE)
    cursor.execute("INSERT INTO stats (name, age, Tm, Pos, GP, G, A, PTS, PLUS_MINUS, PIM, year) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (data["name"], data["age"], data["Tm"], data["Pos"], data["GP"], data["G"], data["A"], data["PTS"], data["PLUS_MINUS"], data["PIM"], data["year"]))
    connection.commit()
    cursor.close()
    return {"message": "stats added successfully."}
# get all data points from the stats table 
@app.get("/api/stats/getAll")
def get_all_stats():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM stats")
    stats = cursor.fetchall()
    cursor.close()
    return {"stats": stats}
# * get specific player stats by name

def get_player_stats(name, year):
    year = int(year)
    name = name.lower()
    #query the database for the player
    cursor = connection.cursor()
    #fetch all the player stats than look for the name value using regex
    cursor.execute("SELECT * FROM stats WHERE year=?", (year,))
    stats = cursor.fetchall()
    cursor.close()
    player_stats = None

    for stat in stats:
        #grab the name value from row
        name_value = stat[1]
        
        #split it into a list of words
        name_value = tk.word_tokenize(name_value)
        
        #loop through the list of words
        for word in name_value:
            word = word.lower()
            #if the word matches the name we are looking for return the stats
            if(word == name):
                player_stats = stat
            

    if(player_stats == None):
        return
    else:
        return player_stats

#* delete a player from the stats table 
@app.post("/api/stats/deletePlayer")
def delete_player_stats():
    name = request.get_json()["name"]
    cursor = connection.cursor()
    cursor.execute("DELETE FROM stats WHERE name=%s", (name,))
    connection.commit()
    cursor.close()
    return {"message": "player deleted successfully."}


# ! ################################################
# * chat bot post and get methods 

# get method to re-initialize the bot
@app.get("/api/chatbot/init")
def chat_bot_init():
   #call init method
   bot.__init__()
   
   
   return {"message": "bot initialized successfully."}






#import the bot wrapper

#initialize the bot
bot = BotWrapper()

#method to get the response from the bot
@app.post("/api/chatbot/chat")
def chat_bot():
    #input form should be an array with a message and an identifier 
    data = request.get_json()

    #get the message
    message = data["message"]

    #get the identifier
    identifier = data["identifier"]
    input = [message, identifier]
    
    #convert the input if it is ment to be of type int to type in \
    if(identifier == "G" or identifier == "A" or identifier == "PTS" or identifier == "plusMinus" or identifier == "PIM" or identifier == "GP"):
        input[0] = int(input[0])
    
    #error handling for invalid inputs 
    isValid = validate_input(input)
    if(isValid == False):
        return {"message": "invalid input",
                "code": identifier}

    

    


    response = None
    #pass the data to the bot when the position is selected
    if(identifier == "position"):
        if(message == "D"):
            input = ["1", "position_D"]
            response = bot.initialize(input)
            input = ["0", "position_LW"]
            response = bot.initialize(input)
        elif(message == "LW"):
            input = ["0", "position_D"]
            response = bot.initialize(input)
            input = ["1", "position_LW"]
            response = bot.initialize(input)
        else:
            input = ["0", "position_D"]
            response = bot.initialize(input)
            input = ["0", "position_LW"]
            response = bot.initialize(input)
    else:
        response = bot.initialize(input)

    awns = response[0]
    code = response[1]
    print(code)
    #handel player stats search
    if(code == 767):
        print(awns)
        player = player_search_call(awns)
        if(player != None):
            awns = player
            # * parse out the player library into a string 
            awns = "in %s, %s played %s games, had %s goals, %s assists, and %s points. His plus Minus score was, %s" % (player["year"], player["name"], player["GP"], player["G"], player["A"], player["PTS"], player["plusMinus"])
            code = 400
            bot.__init__()
            return {
            "response": awns,
            "code": code
            }
        else:
            awns = "Player not found"
            code = 401
            return {
            "response": awns,
            "code": code
            }
    
    

    #check for if the code is Positon_d or Position_LW
    if(code == "position_D" or code == "position_LW"):
        awns = "Please Entre the position of a player \n C: centre \n LW: left wing \n RW: right wing \n D: defence \n"
        code = "position"



    #return the response with the code 
    if code == 400:
        bot.__init__()
    return {"response": awns,
            "code": code}
    
    

def validate_input(data):
    #get the identifier
    identifier = data[1]

    #switch case to check the identifier
    match identifier:
        case "name":
            #check to make sure that the input is a string
            if(isinstance(data[0], str)):
                return True
            else:
                return False
            
        case "G":
            #ensure type is int
            if(isinstance(data[0], int)):
                return True
            else:
                return False

        case "A":
            #ensure type is int
            if(isinstance(data[0], int)):
                return True
            else:
                return False

        case "PTS":
            #ensure int or float 
            if(isinstance(data[0], int) or isinstance(data["message"], float)):
                return True
            else:
                return False
        case "PIM":
            #ensure int or float 
            if(isinstance(data[0], int) or isinstance(data["message"], float)):
                return True
            else:
                return False

            
        case "PLUS_MINUS":
            #ensure int or float 
            if(isinstance(data[0], int) or isinstance(data["message"], float)):
                return True
            else:
                return False
        case "GP":
            #ensure type is int
            if(isinstance(data[0], int)):
                return True
            else:
                return False
        case "position":
            if(isinstance(data[0], str)):
                return True
            else:
                return False
        case "string":
            return True

        

#!things to fix 

#1. fix init method it is not re setting the bot completely (should be working now)

#2. fix the position method it is not working properly (working)

#3. add db to get stats methods 

#!