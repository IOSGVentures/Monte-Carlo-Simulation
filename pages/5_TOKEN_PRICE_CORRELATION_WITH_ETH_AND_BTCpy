import numpy as np
import altair as alt
import pandas as pd
import streamlit as st
import requests
import json
import matplotlib
from matplotlib import pyplot as plt
# Set the maximum number of open figures to 30
matplotlib.rcParams['figure.max_open_warning'] = 30
import numpy as np
import pandas as pd
import yfinance as yf
import datetime 
import matplotlib.dates as mdates
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()
from numerize.numerize import numerize

st.set_page_config(page_title="Multiple project performance timeseries", page_icon="🧐", layout="wide")
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
# --- USER AUTHENTICATION ---
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')
elif authentication_status:
    
    # ---- SIDEBAR ----
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome {name}")
    
    
    # ---- MAINPAGE ----
    st.title(":earth_asia: Token Price Correlation with ETH and BTC")
    st.markdown("##")
    def projects_corr_with_eth_btc(project_id, start_date):

      def get_data(data):
          date = []
          price = []
          for i in range(len(data)):
              date.append(pd.to_datetime((data[i]['timestamp'])))
              price.append(data[i]['price'])
          dataa = [price]
          df = pd.DataFrame(dataa, columns=date, index=['price'])
          df = df.T.dropna()
          return df

      headers = {"Authorization": "Bearer 3365c8fd-ade3-410f-99e4-9c82d9831f0b"}

      project_ids = ['bitcoin','ethereum']

      url = f"https://api.tokenterminal.com/v2/projects/{project_id}/metrics?metric_ids=price"
      response = requests.get(url, headers=headers)
      data_shows = json.loads(response.text)
      data = data_shows['data']
      df = get_data(data)
      df = df[f'{start_date}':]
      df.rename(columns={'price': f'price_{project_id}_usd'}, inplace=True)

      for i, project in enumerate(project_ids):
          url = f"https://api.tokenterminal.com/v2/projects/{project}/metrics?metric_ids=price"
          response = requests.get(url, headers=headers)
          data_shows = json.loads(response.text)
          data = data_shows['data']
          df1 = get_data(data)
          df1 = df1[f'{start_date}':]
          df1.rename(columns={'price': f'price_{project}'}, inplace=True)
          df = pd.concat([df, df1], axis=1)
      df['rolling_correlation_eth'] = df[f'price_{project_id}_usd'].rolling(window=30).corr(df[f'price_ethereum'])
      df['rolling_correlation_btc'] = df[f'price_{project_id}_usd'].rolling(window=30).corr(df[f'price_bitcoin'])
      df = df[::-1]

      fig, ax = plt.subplots(figsize=(18, 8))
      ax2 = ax.twinx()

      df['rolling_correlation_eth'].plot(color='crimson', ax=ax, label=f'{project_id} correlation with ETH')
      df['rolling_correlation_btc'].plot(color='blue', ax=ax2, label=f'{project_id} correlation with BTC')

      ax.set_xlabel('Date', fontsize=20)
      ax.set_ylabel(f'Ethereum price and {project_id} price correlation', color='crimson', fontsize=20)
      ax2.set_ylabel(f'Bitcoin price and {project_id} price correlation', color='blue', fontsize=20)

      handles, labels = ax.get_legend_handles_labels()
      handles2, labels2 = ax2.get_legend_handles_labels()
      ax2.legend(handles + handles2, labels + labels2, loc='upper right', fontsize=20)

      plt.title(f'{project_id} token price correlation with ETH and BTC', fontsize=30)

      return fig

    	
#with st.form("my_form",clear_on_submit=False):
    
project_id = st.text_input('Enter the project ID from Token Terminal', key='1')
date = st.date_input("Start Date", value=pd.to_datetime("2022-01-31", format="%Y-%m-%d"))

with st.form("monte_carlo_form"):
    if st.form_submit_button("Submit"):
        st.header(f"Here's Timeseries with token price correlation with ETH and BTC for {project_id.capitalize()}!")
        f1 = projects_corr_with_eth_btc(project_id, date)
        
        st.pyplot(f1)
