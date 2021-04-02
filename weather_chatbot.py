# -*- coding: utf-8 -*-
"""
Created on Sun Mar 28 10:57:59 2021

@author: Pratham
"""


# Import required libraries
from googletrans import Translator
import nltk
nltk.download('stopwords', quiet=True)
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import string
from pyowm import OWM
from datetime import datetime
import requests
import json


# Predefined queries for chatbot
queries = ['what is the weather today',
           'what is the temperature today',
           'what is the maximum / highest temperature today',
           'what is the minimum / lowest temperature today',
           'what is the chance of rain today',
           'what is the chance of rain tomorrow',
           'what is the weather forecast for today',
           'what is the weather forecast for tomorrow',
           'what time is the sunset today',
           'what time is the sunrise tomorrow']


# Create Translator object for translation and set target language
translator = Translator()
target_lang = 'gu'


# Configure PyOWM with OpenWeatherMap API key
APIKEY = 'YOUR-OWM-API-KEY'
owm = OWM(APIKEY)
mgr = owm.weather_manager()


# Function to translate user query to English
def translate_to_EN(user_query):
    return translator.translate(user_query, dest='en').text.lower()


# Function to translate result to target language
def translate_to_target_language(result):
    return translator.translate(result, dest=target_lang).text


# Function to remove punctuations, tokenize text and stem words in text
def tokenize(text):
    text = text.translate(str.maketrans('', '', string.punctuation))
    ps = PorterStemmer()
    tokens = []
    for token in text.split():
        tokens.append(ps.stem(token))
    return tokens


# Function to remove English stopwords from text
def remove_stopwords(tokenized_text):
    stopwords_EN = stopwords.words('english')
    return set([word for word in tokenized_text if word not in stopwords_EN])


# Function to calculate Jaccard similarity between 2 texts
def jaccard_similarity(set1, set2):
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection)/len(union)


# Function to determine query which is most similar to user query
def most_similar_query(user_query_tokens):
    highest_sim_score = 0.0
    most_sim_query = ''
    for query in queries:
        query_tokens = remove_stopwords(tokenize(query))
        sim_score = jaccard_similarity(user_query_tokens, query_tokens)
        if sim_score>highest_sim_score:
            highest_sim_score = sim_score
            most_sim_query = query
    return most_sim_query


# Function to get user location through ipdata API
def get_user_location():
    ipdata = requests.get('https://api.ipdata.co?api-key=YOUR-IPDATA-API-KEY').json()
    return ipdata['city']


# Function to get weather information based on query
def weather_info(query):
    user_city = get_user_location()
    weather_data = mgr.weather_at_place(user_city).weather
    forecast_3h = list(mgr.forecast_at_place(user_city, '3h').forecast)

    if query in queries:
        index = queries.index(query)
    else:
        index = -1
    if index==0:
        status = str(weather_data.detailed_status)
        current_temp = str(weather_data.temperature('celsius')['temp'])
        max_temp = str(weather_data.temperature('celsius')['temp_max'])
        min_temp = str(weather_data.temperature('celsius')['temp_min'])
        humidity = str(weather_data.humidity)
        result = status.capitalize() + " today. Current temperature is " + current_temp + " degrees celsius (Maximum: " + max_temp + "*C, Minimum: " + min_temp + "*C). Humidity today is " + humidity + "%."
        return result
    elif index==1: 
        current_temp = str(weather_data.temperature('celsius')['temp'])
        result = "The current temperature is " + current_temp + " degrees celsius."
        return result
    elif index==2:
        max_temp = str(weather_data.temperature('celsius')['temp_max'])
        result = "The maximum temperature today is " + max_temp + " degrees celsius."
        return result
    elif index==3:
        min_temp = str(weather_data.temperature('celsius')['temp_min'])
        result = "The minimum temperature today is " + min_temp + " degrees celsius."
        return result
    elif index==4:
        rain_today = weather_data.rain
        if len(rain_today)==0:
            result = "There is no chance of rain today."
        else:
            result = "Rain today is " + str(rain_today['1h']) + "."
        return result
    elif index==5:
        rain_tomorrow = weather_data.rain
        if len(rain_tomorrow)==0:
            result = "There is no chance of rain tomorrow."
        else:
            result = "Rain tomorrow will be " + str(rain_tomorrow['1h']) + "."
        return result
    elif index==6:
        status = str(forecast_3h[-1].detailed_status)
        result = status.capitalize() + " forecasted today."
        return result
    elif index==7:
        status = str(forecast_3h[-1].detailed_status)
        result = status.capitalize() + " forecasted tomorrow."
        result = ''
        return result
    elif index==8:
        sunset_time_unix = weather_data.sunset_time() + 19800
        sunset_time = str(datetime.fromtimestamp(sunset_time_unix).strftime('%H:%M:%S'))
        result = "Time of sunset today is " + sunset_time + "."
        return result
    elif index==9:
        sunrise_time_unix = weather_data.sunrise_time() + 19800
        sunrise_time = str(datetime.fromtimestamp(sunrise_time_unix).strftime('%H:%M:%S'))
        result = "Time of sunrise tomorrow will be " + sunrise_time + "."
        return result
    else:
        result = "I am sorry, I don't understand your question."
        return result
    
    
# Function to greet user at start of chat
def greet():
    greeting = translator.translate("Hello! I am your weather assistant. \nAsk me queries related to weather. \nTo end this chat, say 'goodbye'.", dest=target_lang).text
    print('\n', greeting)
    

# Function to say goodbye to user at end of chat
def goodbye():
    goodbye = translator.translate("Goodbye! Have a nice day!", dest=target_lang).text
    print('\n', goodbye)
    

# Function to run chatbot
def run():
    talking = True
    greet()
    while(talking):
        prompt = translator.translate("Ask your query here", dest=target_lang).text
        user_query_GJ = input(prompt + ": ")
        user_query_EN = translate_to_EN(user_query_GJ)
        if user_query_EN=='goodbye' or user_query_EN=='see you soon':
            talking = False
            break
        else:
            user_query_EN_tokens = remove_stopwords(tokenize(user_query_EN))
            chatbot_query = most_similar_query(user_query_EN_tokens)
            output = translate_to_target_language(weather_info(chatbot_query))
            print(output)
    goodbye()
    return


# Driver code
if __name__ == '__main__':
    run()
