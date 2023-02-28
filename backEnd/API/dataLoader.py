import app
import pandas as pd
import requests
import time
#import final data csv file Model\Final_Data.csv
data = pd.read_csv("playerStats.csv")

print(data.head())
#loop through data and add each player to the database
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
        
    

