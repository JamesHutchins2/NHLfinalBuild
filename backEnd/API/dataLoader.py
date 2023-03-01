import app
import pandas as pd
import requests
import time
#import final data csv file Model\Final_Data.csv
data = pd.read_csv("stats.csv")
#remove 2017 and 2018 data
data = data[data.year != 2017]
data = data[data.year != 2018]

print(data.head())
#loop through data and add each player to the database
#change column names 

for index, row in data.iterrows():
    #check to see if player in db
    isPlayer = requests.get("http://localhost:5000/api/stats/getPlayerStats", json={"name": row["Player"]})
    if(isPlayer != None):
        continue
    else:
        #add player to database
        #send a post request to the API to add the player
        requests.post("http://localhost:5000/api/stats/insert", json={
            "name": row["Player"],
            "age": row["Age"],
            "Tm": row["Tm"],
            "Pos": row["Pos"],
            "GP": row["GP"],
            "G": row["G"],
            "A": row["A"],
            "PTS": row["PTS"],
            "PLUS_MINUS": row["+/-"],
            "PIM": row["PIM"],
            "year": row["year"]
        })
        # !fix adding name to reposne 
    

"""@app.get("/data/importCSV")
def import_csv():
    #read a csv file and add it to the database
    data = pd.read_csv("stats.csv")
    #rename columns
    #make position column into 2 dummy var columns called position_D and position_LW
    data["position_D"] = data["Pos"].apply(lambda x: 1 if x == "D" else 0)
    data["position_LW"] = data["Pos"].apply(lambda x: 1 if x == "LW" else 0)
    #drop the position column
    data = data.drop(columns=["Pos"])
    data = data.rename(columns={"Player": "name", "GP": "games_played", "+/-": "plus_minus", "PTS": "points", "PIM": "penalty_minutes", "G": "goals", "A": "assists", "Age": "age", "Tm": "team" })
    #add a column for the model result set to zero
    data["model_result"] = 0
    cursor = connection.cursor()
    #create table if it does not exist
    cursor.execute(CREATE_PLAYERS_MODEL_TABLE)
    for index, row in data.iterrows():
        #check that player does not already exist
        cursor.execute("SELECT * FROM players WHERE name=?;", (row["name"],))
        
        if(cursor.fetchone() == None):
            cursor.execute(INSERT_PLAYER, (row["name"], row["games_played"], row["goals"], row["penalty_minutes"], row["position_D"], row["position_LW"], row["model_result"]))
        else:
            continue"""
# ! this code was used to upload the data to the database