#https://www.hockey-reference.com/leagues/NHL_2018_skaters.html
from collections import Counter
from responses import step1_responses, blank_spot
from user_functions import preprocess, compare_overlap, pos_tag, extract_nouns, compute_similarity
import joblib
import pandas as pd
import nltk
import json
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



class ChatBot:

    #if we see a exit command we will end the instance of the chatbot
    # ! this will need to be changed to be a method that will simply re initialize the bot
    def make_exit(self):
        
        return True
    
    #original call method that runs that chatbot 
    # ! we will just have this as the start of the chatbot every time it is init so with the above 
    def chat(self):
        print('\nHello, this is a retrieval based chat bot created by Ethan OBrien\n')
        user_message=input("""These are the current functions I am capable of:\n
        1.) I can provide you a players NHL stats given their name\n
        2.) I can predict if a player will be drafted in the NHL first round given their junior stats
        \nHow can I help you today?\n""")

        #this continues the coversaiton until the user says goodbye
        while not self.make_exit(user_message):
            user_message = self.respond(user_message)

    #this method determines the intent of the user, we will want to store this in the instacne after it determines
    # @ ouce we have the intent we will want to call the appropriate method to handle the intent
    # we will then have to update it back to unknown so that the next time we call it we can determine the intent again
    def find_intent_match_step1(self,step1_responses,user_message):
        bow_user_message=Counter(preprocess(user_message))
        processed_responses = [Counter(preprocess(response)) for response in step1_responses]
        similarity_list=[compare_overlap(response,bow_user_message) for response in processed_responses]
        response_index=similarity_list.index(max(similarity_list))
        return step1_responses[response_index],response_index

    #this method calls find intent and returns it to the chat method
    def respond(self,user_message):
        best_response_step1, response_index=self.find_intent_match_step1(step1_responses,user_message)
        return {
            "intent": response_index,
            "response": best_response_step1
        }
        
    #! we take the user input if the intent is 0 we will call the get stats method    
    def get_stats_call(self,user_message):
        
        return [user_message,767]
                        


        
        
    # this method is no longer important as we cannot pass the data base to the the front end          
    def get_graphs(self,model_list,probs_lis):
        fig=plt.figure(figsize=(10,5))
        sns.barplot(x=model_list,y=probs_lis)
        plt.xlabel('Model Type')
        plt.ylabel('Probability (%)')
        ax = plt.gca()
        ax.set_ylim(0, 100)
        sns.set_context("notebook", font_scale=0.3)
        plt.show()
        plt.close()
        
    # we will have to make this spit out the prediction values in a library
    def get_predictions(self,name,G,A,GP,PIM,position_D,position_LW):
       
        loaded_scaler = joblib.load('scaler.joblib')
        x_titles=['G','A','GP','PIM','position_D','position_LW']
        # ! re adapt this to call the data base 
        user_input_data = pd.DataFrame(data=[[G,A,GP,PIM,position_D,position_LW]], columns=x_titles)
        scaled_user_input_data = loaded_scaler.transform(user_input_data)
        scaled_user_input_data = pd.DataFrame(data=scaled_user_input_data, columns=x_titles)
        user_input_data_single_row = scaled_user_input_data.iloc[0, :]
        user_input_data_single_row_array = user_input_data_single_row.to_numpy().reshape(1, -1)

        rf_dt_model= joblib.load('random_forest_model.joblib')
        rf_prediction = rf_dt_model.predict(user_input_data_single_row_array)[0]
        rf_prediction_prob=(rf_dt_model.predict_proba(user_input_data_single_row_array)[0][1]*100).round(2)
        #rf_prediction_prob
        
        bag_svm_model= joblib.load('bag_svm_model.joblib')
        svm_prediction = bag_svm_model.predict(user_input_data_single_row_array)[0]
        svm_prediction_prob=(bag_svm_model.predict_proba(user_input_data_single_row_array)[0][1]*100).round(2)
        #svm_prediction_prob
        #dtree_prediction_prob
        #rf_prediction_prob
        #lr_prediction_prob
        #sim_mlp_prediction_prob
        #com_mlp_prediction_prob
        bag_dtree_model= joblib.load('bag_dtree_model.joblib')
        dtree_prediction = bag_dtree_model.predict(user_input_data_single_row_array)[0]
        dtree_prediction_prob=(bag_dtree_model.predict_proba(user_input_data_single_row_array)[0][1]*100).round(2)
        #dtree_prediction_prob


        bag_lr_model= joblib.load('bag_lr_model.joblib')
        lr_prediction = bag_lr_model.predict(user_input_data_single_row_array)[0]
        lr_prediction_prob=(bag_lr_model.predict_proba(user_input_data_single_row_array)[0][1]*100).round(2)
        


        simple_MLP_model= tf.keras.models.load_model('simple_MLP_model.h5')
        sim_mlp_prediction=simple_MLP_model.predict(user_input_data_single_row_array,verbose=False).round()[0][0]
        sim_mlp_prediction_prob=(simple_MLP_model.predict(user_input_data_single_row_array,verbose=False)[0][0]*100).round(2)
        

        complex_MLP_model= tf.keras.models.load_model('complex_MLP_model.h5')
        com_mlp_prediction=complex_MLP_model.predict(user_input_data_single_row_array,verbose=False).round()[0][0]
        com_mlp_prediction_prob=(complex_MLP_model.predict(user_input_data_single_row_array,verbose=False)[0][0]*100).round(2)
        

        prediction_list=[rf_prediction,svm_prediction,dtree_prediction,lr_prediction,sim_mlp_prediction,com_mlp_prediction]
        models_list=['Random Forest','Support Vector Machine','Decision Tree','Logistic Regression','Simple MLP Deep Learning','Complex MLP Deep Learning']
        
        probs_list=[rf_prediction_prob,svm_prediction_prob,dtree_prediction_prob,lr_prediction_prob,sim_mlp_prediction_prob,com_mlp_prediction_prob]
        prediction=statistics.mode(prediction_list)
        avg_prob=np.mean(probs_list).round(2)

        if prediction==1:
            prediction_message =  avg_prob
        else: 
            prediction_message =  100-avg_prob

        probs_list={
            "rf_prediction_prob":rf_prediction_prob ,
            "svm_prediction_prob": svm_prediction_prob,
            "dtree_prediction_prob": dtree_prediction_prob,
            "lr_prediction_prob": lr_prediction_prob,
            "sim_mlp_prediction_prob": sim_mlp_prediction_prob,
            "com_mlp_prediction_prob": com_mlp_prediction_prob,
            "predictionProb":prediction_message
            }
        returnSting = "the rf model predicts that " + name + " has a " + str(rf_prediction_prob) + "chance of being drafted." + "the svm model predicts that " + name + " has a " + str(svm_prediction_prob) + "%" + " chance of being drafted." + "the dtree model predicts that " + name + " has a " + str(dtree_prediction_prob) + "%"+ " chance of being drafted." + "the lr model predicts that " + name + " has a " + str(lr_prediction_prob) + "%"+" chance of being drafted." + "the simple mlp model predicts that " + name + " has a " + str(sim_mlp_prediction_prob) + "%"+" chance of being drafted." + "the complex mlp model predicts that " + name + " has a " + str(com_mlp_prediction_prob) + "%"+" chance of being drafted."
        return returnSting
    #add app.py to path
    
    

    def get_stats(self,user_message):
        #lets change this function so that it queries the database from app.py
        # to do this we will have to import the get request from app.py
       

        # ! here we preprocess the user message
        

        # ! here we have not found a player so return None
        if entity==None:
            return {"message": "I'm sorry, I could not find that player. Could you please try again?\n",
            "index": 1}
             
        
        player_stats = entity
        print(player_stats)
            
        
        player_stats = {
                        "Age": int(player_stats['Age'].values[0]),
                        "G": int(player_stats['G'].values[0]),
                        "Tm": player_stats['Tm'].values[0],
                        "Pos": player_stats['Pos'].values[0],
                        "GP": int(player_stats['GP'].values[0]),
                        "A": int(player_stats['A'].values[0]),
                        "PTS": int(player_stats['PTS'].values[0]),
                        "plusMinus": int(player_stats['+/-'].values[0]),
                        "PIM": int(player_stats['PIM'].values[0]),
                        "year": int(player_stats['year'].values[0])

                    }
                    #covert to json
        player_stats = json.dumps(player_stats)
                    

                    
        return {
            "data":player_stats,
            "index": -1
            }


    def find_entities(self,user_message):
        tagged_user_message=pos_tag(preprocess(user_message))
        message_nouns=extract_nouns(tagged_user_message)
        tokens=word2vec(' '.join(message_nouns))
        category=word2vec(blank_spot)
        word2vec_result=compute_similarity(tokens,category)
        word2vec_result.sort(key=lambda x: x[2])
        if len(word2vec_result) < 1:
          return blank_spot
        else:
         return word2vec_result[-1][0]


