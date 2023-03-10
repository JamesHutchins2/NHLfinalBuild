<h1>NHL Chat Bot API Docs</h1>
<hr>
<h2>Introduction</h2>
<h2>API End Points</h2>
<p>There are many end points in this api and I will try and cover the most important ones. </p>
<ul>
<li>/api/chatbot/chat</li>
<p>This is the main end point that works with the chat bot front end to communicate with the various models. This is the only one that really matters for using the API as all other end points and methods are really just utilities for manipulating the data base </p>
<li>/api/chatbot/init</li>
<p>This end point can be called to simply re create a new instance of the chat bot wrapper class and therefore of the chat bot it's self </p>
<li>get_player_stats</li>
<li>/api/stats/getAll</li>
<li>/api/stats/insert</li>
<li>player_search_call</li>
<li>/api/allplayers</li>
<li>/data/addBulk</li>
<li>/data/addPlayers</li>
<li>/api/player</li>
</ul>

<h2>Stats Search</h2>
<p>Stats for this model are stored on an AZURE data base. As a result this functionality is primarily handled on by the API instead of the chat bot it's self. Ounce the initialize function has been called if it is a stats search case the functions within the chat bot simply call back the player_search_call function in the api. This function then parses year and name from the message given by the user and queries the data base for such player. This value is then passed back through to the chat api call and returned to the user. </p>
<h2>Prediction Function</h2>
<h2>Bot Wrapper class</h2>
<p>The bot wrapper class allows the api to work with the various models. It does this by routing all api calls through a single function called initalize. The function hold the detected intent state of the user in a class instance variable. This allows the API call to route through this same function each time and move to the correct point depending on the detected user intent in the given call. an intent of -1 means that it is unknown (default case). 0 means that the user is looking for player stats and 1 indicated that prediction of draft round  </p>

```python
print("Hello World")

```

::: mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
:::
```mermaid
stateDiagram
    [*] --> First
    state First {
        [*] --> second
        second --> [*]
    }
```

"name": player[1],
                            "Age": int(player[2]),
                            "G": int(player[6]),
                            "Tm":   player[3],
                            "Pos": player[4],
                            "GP": player[5],
                            "A": player[7],
                            "PTS": player[8],
                            "plusMinus": int(player[9]),
                            "PIM": int(player[10]),
                            "year": int(player[11])