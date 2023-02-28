from test_main import ChatBot
#https://www.hockey-reference.com/leagues/NHL_2018_skaters.html
from collections import Counter
from responses import step1_responses, blank_spot
from user_functions import preprocess, compare_overlap, pos_tag, extract_nouns, compute_similarity
import joblib
import pandas as pd
import nltk
import tensorflow as tf
import statistics
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import logging
logging.getLogger("tensorflow").setLevel(logging.ERROR)
import seaborn as sns
from matplotlib import pyplot as plt
nltk.download('punkt',quiet=True)
nltk.download('averaged_perceptron_tagger',quiet=True)
import sys
import spacy
word2vec = spacy.load('en_core_web_sm')
exit_commands = ("quit", "goodbye", "exit",'no')

#this is a wrapper class for the chatbot
#it will allow use to make api calls to communicate with the chatbot


class BotWrapper:
    #define instance vars 
    inputs = []
    outputs = []
    intentState = -1
    predictionKnowns = {}
    predictionCall = None

    #define constructor
    def __init__(self):
        self.bot = ChatBot()
        self.inputs = []
        self.outputs = []
        self.intentState = -1
        self.predictionKnowns = {
            "name": None,
            "G": None,
            "A": None,
            "GP": None,
            "PIM": None,
            "position_D" : None,
            "position_LW" : None
        }
        predictionCall = self.predictionCall
  


    #this method will be used to clear the instance of the bot

    # ! this class is the main handler for the given user inputs   
    def initialize(self,ur):
        #get the intent state
        state = self.intentState

        
        # all items passed to this class should be a list of two items
        # the first item is the user input
        # the second item is the class of the user input default is "string"
        user_input = ur[0]
        inputClass = ur[1]
        

        self.inputs.append(user_input)
        #first we check what the intent state is 
        #if it is -1 then we are in the initial state
        if self.intentState == -1:
            #we dont yet know what the user wants
            #get the response from that bot
            response = self.bot.respond(user_input)

            #extract message and index
            message = response["response"]
            self.outputs.append(message)
            index = response["intent"]

            if index == -1:
                #log the output 
                self.outputs.append(message)
                #set the intent state (must already be -1)
                return message
            else:
                #re set the intent state
                self.intentState = index
                

        #IN THE CASE THAT THE BOT DETERMINES THE USER WANTS PLAYER STATS
        if self.intentState == 0:

            
            #we will call the function with this user input
            stats_response = self.bot.get_stats_call(user_input)
            
            #define the message
            message = stats_response

            #add the message to the outputs log
            self.outputs.append(message)
            # !we have to fix
            #simply push back response
            return [stats_response[0], stats_response[1]]

        #IN THE CASE THAT THE BOT DETERMINES THE USER WANTS TO MAKE A PREDICTION
        if self.intentState == 1:
            #we will call the function with this user input, and the input class
            return self.predictionCall(user_input , inputClass)
           

        else:
            #405 is the error code for the intent state not being found
            return 405

        

    def predictionCall(self, userInput, inputClass):
        #we will need a series of inputs from the user to complete this proccess
        #to determine what is required we will use the prediction knowns list
        # * (name,G,A,GP,PIM,position_D,position_LW)
        #self.predictionKnowns = {
        #    "name": None,
        #    "G": None,
        #    "A": None,
        #    "GP": None,
        #    "PIM": None,
        #   "position_D" : None,
        #    "position_LW" : None
        #}
        #we will take the user input now and place it into the prediction knowns list
        # ! we will have to take an array input with an indicator of what we have received 
        # ! as a result we will have to first look at what data type has been given

        # make a switch case that takes the input class and then places the input into the correct spot
        # * (name,G,A,GP,PIM,position_D,position_LW)
        if inputClass == "name":
            #we have received the name of the player
            self.predictionKnowns["name"] = userInput
        elif inputClass == "G":
            #we have received the number of goals
            self.predictionKnowns["G"] = userInput
        elif inputClass == "A":
            #we have received the number of assists
            self.predictionKnowns["A"] = userInput
        elif inputClass == "GP":
            #we have received the number of games played
            self.predictionKnowns["GP"] = userInput
        elif inputClass == "PIM":
            #we have received the number of penalty minutes
            self.predictionKnowns["PIM"] = userInput
        elif inputClass == "position_D":
            #we have received the position of the player
            self.predictionKnowns["position_D"] = userInput
        elif inputClass == "position_LW":
            #we have received the position of the player
            self.predictionKnowns["position_LW"] = userInput
       
        if self.predictionKnowns["name"] == None:
            #we need to get the name of the player
            #the number at the end of the return will allow the front end to know what we are looking for 

            return ["What is the name of this player?", "name"]
        
        if self.predictionKnowns["G"] == None:
            #we need to get the number of goals
            return ["How many goals did the player score?", "G"] 
        
        if self.predictionKnowns["A"] == None:
            #we need to get the number of assists
            return ["How many assists did the player have?", "A"]
        
        if self.predictionKnowns["GP"] == None:
            #we need to get the number of games played
            return ["How many games did the player play?", "GP"]
        
        if self.predictionKnowns["PIM"] == None:
            #we need to get the number of penalty minutes
            return ["How many penalty minutes did the player have?", "PIM"]
        
        if self.predictionKnowns["position_D"] == None:
            #we need to get the position of the player
            return ["Does the player play defence?", "position_D"]
        
        if self.predictionKnowns["position_LW"] == None:
            #we need to get the position of the player
            return ["does the player play left wing?", "position_LW"]
        
        #if this point is reached then we have all the information we need to make a prediction
        botPredictions = self.bot.get_predictions(
            self.predictionKnowns["name"],
            self.predictionKnowns["G"],
            self.predictionKnowns["A"],
            self.predictionKnowns["GP"],
            self.predictionKnowns["PIM"],
            self.predictionKnowns["position_D"],
            self.predictionKnowns["position_LW"]
            )
        #we will reset the intent state
        self.intentState = -1
        #we will reset the prediction knowns
        return [botPredictions, 400]


#lets try to make a chatbot

