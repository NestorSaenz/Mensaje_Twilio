import os
import os
from twilio.rest import Client
from twilio_config import *
import time

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime

# Armado de la URL

query = 'Medellin'
api_key = API_KEY_WAPI
url_clima = 'http://api.weatherapi.com/v1/forecast.json?key='+api_key+'&q='+query+'&days=1&aqi=yes&alerts=no'

#Ahora se hace la peticion con la libreria requests, y
#esa respuesta se convierte en un archivo JSON

response = requests.get(url_clima).json()

# DataFrame
# Funcion para extraer cada uno de los campos de los 24 los registros del wheather api

def get_forecast(response, i):
    date = response['forecast']['forecastday'][0]['hour'][i]['time'].split()[0]
    hour = int(response['forecast']['forecastday'][0]['hour'][i]['time'].split()[1].split(':')[0])
    condition = response['forecast']['forecastday'][0]['hour'][i]['condition']['text']
    temperature = response['forecast']['forecastday'][0]['hour'][i]['temp_c']
    rain = response['forecast']['forecastday'][0]['hour'][i]['will_it_rain']
    prob_rain = response['forecast']['forecastday'][0]['hour'][i]['chance_of_rain']
    
    return date, hour, condition, temperature, rain, prob_rain
# se hace un ciclo for para extraer los datos, con el uso d ela libreria tqdm, 
# que permite visualizar  un porcentaje de carga

datos = []

for i in tqdm(range(len(response['forecast']['forecastday'][0]['hour'])), colour = 'green'):
    datos.append(get_forecast(response, i))

# Creacion del DataFrame

col = ['Date','Hour', 'Condition', 'Temperature', 'Rain', 'prob_rain']
df = pd.DataFrame(datos, columns = col)

# Se filtra el dataframe por los periodos donde hay lluvia y el tiempo entre las 6 am y 10 pm

df_rain = df[(df['Rain'] == 1) & (df['Hour'].between(6,22))]
df_rain = df_rain[['Hour', 'Condition']]
df_rain.set_index('Hour', inplace= True)
df_rain

# Mensaje -Template
mensaje_ ='\nHola! \n\n\n El pronostico del tiempo hoy ' + df['Date'][0] +' en '+ query + ' es: \n\n\n ' + str(df_rain)

#Mensaje SMS desde twilio

account_sid = TWILIO_ACCOUNT_SID
auth_token = TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                    body= mensaje_,
                    from_ = PHONE_NUMBER,
                    to = '+573012616255'
                )
                

print(f'Mensaje enviado {message.sid}')