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

# ! #############
#here we will import all the player names to make the calls to db faster

player_names = pd.read_csv("pn.csv")
#split into first and last name
player_names["first_name"] = player_names["Player"].apply(lambda x: x.split(" ")[0])
player_names["last_name"] = player_names["Player"].apply(lambda x: x.split(" ")[1])

# ! ################################### #############



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
    year = request.get_json()["year"]
    #query the database for the player
    cursor = connection.cursor()
    #check the player and year
    cursor.execute("SELECT * FROM stats WHERE name=%s AND year=%s", (name, year)) 
    player = cursor.fetchone()
    cursor.close()

    if(player == None):
        return  None
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



@app.post("/data/addBulk")
def add_bulk():
    #add an entire list of players to the database
    data = request.get_json()
    cursor = connection.cursor()
    #create table if it does not exist
    cursor.execute(CREATE_PLAYERS_MODEL_TABLE)
    for player in data:
        #check that player does not already exist
        cursor.execute(FIND_PLAYER_byName, (player["name"],))
        if(cursor.fetchone() == None):
            cursor.execute(INSERT_PLAYER, (player["name"], player["games_played"], player["goals"], player["penalty_minutes"], player["position_D"], player["position_LW"], player["model_result"]))
        else:
            continue
    connection.commit()
    cursor.close()
    return {"message": "players added successfully."}
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

#this method is called to find a player by name and year
def player_search_call(user_input):
    #parse user input to find player name
    try:
        year = re.search(r'\d{4}', user_input).group()
    except:
        year = None
    #player holds the player object
    player = None
    #tokenize the user input
    words = tk.word_tokenize(user_input)
    #loop through the words in the user input
    for word in words:
        
        #search for word in player_names
        if(word in player_names["first_name"].values or word in player_names["last_name"].values):
            #if we find a match we call the get_player_stats method
            player = get_player_stats(name=word, year=year)
            if player == None:
                return None
            return player

    





   
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
    if year != None:
        year = int(year)
    else:
        year = "all"

    name = name.lower()
    #query the database for the player
    cursor = connection.cursor()
    #fetch all the player stats than look for the name value using regex
    # * add REGEX pattern to search name faster 
    if(year != "all"):
        cursor.execute("SELECT * FROM stats WHERE year=?", (year,))
        stats = cursor.fetchall()
        cursor.close()
        player_stats = []

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
                    player_stats.append(stat)
                    #! return the stats
                

        if(player_stats == None):
            return "player not found"
        else:
            print(player_stats)
            return player_stats
    else:
        print("no year-------------")
        cursor.execute("SELECT * FROM stats")

        stats = cursor.fetchall()
        cursor.close()
        player_stats = []

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
                    player_stats.append(stat)
                    
                

        if(player_stats == None):
            return "player not found"
        else:
            for stat in player_stats:
                print(stat)
            
            return player_stats



#* delete a player from the stats table 
@app.post("/api/stats/delete")
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

    #check to see if the user wants to exit 

    #parse message word by word
    words = tk.word_tokenize(message)
    #loop through the words
    for word in words:
        #if the word is exit or quit return a message to the user
        if(word == "exit" or word == "quit"):
            print("exit")
            #init chat bot
            bot.__init__()
            return {
                "response": "Goodbye",
                "code": "exit"
                }

    #get the identifier
    identifier = data["identifier"]
    input = [message, identifier]
    
    #convert the input if it is ment to be of type int to type in \
    if(identifier == "G" or identifier == "A" or identifier == "PTS" or identifier == "plusMinus" or identifier == "PIM" or identifier == "GP"):
        try:
            input[0] = int(input[0])
            print("try")
        except:
            print("fail")
            return {
                "response": "Sorry, I didn't understand that. Please Enter a number.",
                "code": identifier
                }
    
    #error handling for invalid inputs 
    isValid = validate_input(input)

    if(isValid == False):
        return {
                "response": "Sorry, Something went wrong. Please try again.",
                "code": identifier
                }

    

    


    response = None
    #pass the data to the bot when the position is selected
    #let's use Regex to grab the first letter of the msg
    first = re.search(r"^[a-zA-Z]", message)
    #convert to string
    if(first != None):
        first = first.group(0)
        first = first.upper()
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
        elif(first == "D"):
            input = ["1", "position_D"]
            response = bot.initialize(input)
            input = ["0", "position_LW"]
            response = bot.initialize(input)
        elif(first == "L"):
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
    
    #handel player stats search
    if(code == 767):
        
        player = player_search_call(awns)
        if(player == None):
            awns = "Sorry, Something went wrong. Please ask for player stats or to predict a player's draft position."
            bot.__init__()
            code = 401
            return {
                "response": awns,
                "code": code
            }
        if(len(player) > 1):
            response = []
            for p in player:
                response.append("in %s, %s played %s games, had %s goals, %s assists, and %s points. His plus Minus score was, %s.      " % (p[11], p[1], p[5], p[6], p[7], p[8], p[9]))
                respone_string = ""
                for r in response:
                    respone_string += r + "     "
            bot.__init__()
            code = 400
            return {
                "response": respone_string,
                "code": code
                }
        
        elif(len(player) == 1):
            response = "in %s, %s played %s games, had %s goals, %s assists, and %s points. His plus Minus score was, %s" % (player[0][11], player[0][1], player[0][5], player[0][6], player[0][7], player[0][8], player[0][9])
            bot.__init__()
            code = 400
            return {
                "response": response,
                "code": code
                }
        else:
                # ! change this 
                awns = "Sorry, Something went wrong. Please ask for player stats or to predict a player's draft position."
                bot.__init__()
                code = 401
                return {
                "response": awns,
                "code": code
                }

        
    
    

    #check for if the code is Positon_d or Position_LW
    if(code == "position_D" or code == "position_LW"):
        awns = "Please Entre the position of "+bot.predictionKnowns["name"]+", C: centre,  LW: left wing, RW: right wing, D: defence"
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

        

