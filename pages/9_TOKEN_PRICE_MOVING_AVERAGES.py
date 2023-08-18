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
    st.title(":earth_asia: Token price and Moving averages")
    st.markdown("##")

    def plot_rolling_averages(project_id, roll_1, roll_2, start_date):
    
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
        #df = df[f'{start_date}':]
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
        df[f'price_{project_id}_eth'] = df[f'price_{project_id}_usd']/df[f'price_ethereum']
        df[f'price_{project_id}_btc'] = df[f'price_{project_id}_usd']/df[f'price_bitcoin']
       # df = df[::-1]
        df = df[f'{start_date}':]
        # Calculate 50, 100, and 200 day moving average
        df[f"{roll_1}_day_MA_USD"] = df[f"price_{project_id}_usd"].rolling(window=roll_1).mean()
        df[f"{roll_2}_day_MA_USD"] = df[f"price_{project_id}_usd"].rolling(window=roll_2).mean()
    
        # Calculate 50, 100, and 200 day moving average
        df[f"{roll_1}_day_MA_ETH"] = df[f"price_{project_id}_eth"].rolling(window=roll_1).mean()
        df[f"{roll_2}_day_MA_ETH"] = df[f"price_{project_id}_eth"].rolling(window=roll_2).mean()
    
        # Calculate 50, 100, and 200 day moving average
        df[f"{roll_1}_day_MA_BTC"] = df[f"price_{project_id}_btc"].rolling(window=roll_1).mean()
        df[f"{roll_2}_day_MA_BTC"] = df[f"price_{project_id}_btc"].rolling(window=roll_2).mean()
    
        dates_usd = []
        for i in range(len(df) - 15):
            if df.iloc[i][f"{roll_2}_day_MA_USD"] > df.iloc[i][f"{roll_1}_day_MA_USD"]:
                if df.iloc[i+1][f"{roll_2}_day_MA_USD"] < df.iloc[i+1][f"{roll_1}_day_MA_USD"]:
                    if (df.iloc[i+1:i+16][f"{roll_2}_day_MA_USD"] < df.iloc[i+1:i+16][f"{roll_1}_day_MA_USD"]).all():
                        dates_usd.append(df.index[i+1])
                #if eth.iloc[i]["Close"] < eth.iloc[i]["200_day_MA"] and eth.iloc[i+14]["Close"] < eth.iloc[i+14]["200_day_MA"]:
                    #if eth.iloc[i+14]["Close"] > eth.iloc[i+14]["200_day_MA"]:
                        #dates.append(eth.index[i+14])
        if dates_usd:
          returns_usd = []
          for date in dates_usd:
              idx = df.index.get_loc(date)
              close_price = df.iloc[idx][f'price_{project_id}_usd']
    
              #if idx + 365 < len(df):
              return_data = {
                "date": date}
              if idx + 30 < len(df):
                return_data["30_day_return"] = (df.iloc[idx+30][f'price_{project_id}_usd'] - close_price) / close_price
              if idx + 45 < len(df): 
                return_data["45_day_return"] = (df.iloc[idx+45][f'price_{project_id}_usd'] - close_price) / close_price
              if idx + 60 < len(df): 
                return_data["60_day_return"] = (df.iloc[idx+60][f'price_{project_id}_usd'] - close_price) / close_price,
              if idx + 75 < len(df):    
                return_data["75_day_return"] = (df.iloc[idx+75][f'price_{project_id}_usd'] - close_price) / close_price,
              if idx + 90 < len(df):    
                return_data["90_day_return"] = (df.iloc[idx+90][f'price_{project_id}_usd'] - close_price) / close_price,
              if idx + 120 < len(df):    
                return_data["120_day_return"] = (df.iloc[idx+120][f'price_{project_id}_usd'] - close_price) / close_price,
              if idx + 150 < len(df):    
                return_data["150_day_return"] = (df.iloc[idx+150][f'price_{project_id}_usd'] - close_price) / close_price,
              if idx + 180 < len(df):    
                return_data["180_day_return"] = (df.iloc[idx+180][f'price_{project_id}_usd'] - close_price) / close_price,
              if idx + 365 < len(df):    
                return_data["365_day_return"] = (df.iloc[idx+365][f'price_{project_id}_usd'] - close_price) / close_pric,
                      
              returns_usd.append(return_data)  
          returns_usd = pd.DataFrame(returns_usd)
    
          average_returns_usd = {
              "30_day_return": (np.prod(1 + returns_usd["30_day_return"]) ** (1 / len(returns_usd["30_day_return"])) - 1) * 100,
              "45_day_return": (np.prod(1 + returns_usd["45_day_return"]) ** (1 / len(returns_usd["45_day_return"])) - 1) * 100,
              "60_day_return": (np.prod(1 + returns_usd["60_day_return"]) ** (1 / len(returns_usd["60_day_return"])) - 1) * 100,
              "75_day_return": (np.prod(1 + returns_usd["75_day_return"]) ** (1 / len(returns_usd["75_day_return"])) - 1) * 100,
              "90_day_return": (np.prod(1 + returns_usd["90_day_return"]) ** (1 / len(returns_usd["90_day_return"])) - 1) * 100,
              "120_day_return": (np.prod(1 + returns_usd["120_day_return"]) ** (1 / len(returns_usd["120_day_return"])) - 1) * 100,
              "150_day_return": (np.prod(1 + returns_usd["150_day_return"]) ** (1 / len(returns_usd["150_day_return"])) - 1) * 100,
              "180_day_return": (np.prod(1 + returns_usd["180_day_return"]) ** (1 / len(returns_usd["180_day_return"])) - 1) * 100,
              "365_day_return": (np.prod(1 + returns_usd["365_day_return"]) ** (1 / len(returns_usd["365_day_return"])) - 1) * 100
          }
    
          average_returns_usd = pd.Series(average_returns_usd)
    
        else:
          average_returns_usd = {}  # Empty dictionary if dates_eth is empty
        dates_eth = []
        for i in range(len(df) - 15):
            if df.iloc[i][f"{roll_2}_day_MA_ETH"] > df.iloc[i][f"{roll_1}_day_MA_ETH"]:
                if df.iloc[i+1][f"{roll_2}_day_MA_ETH"] < df.iloc[i+1][f"{roll_1}_day_MA_ETH"]:
                    if (df.iloc[i+1:i+16][f"{roll_2}_day_MA_ETH"] < df.iloc[i+1:i+16][f"{roll_1}_day_MA_ETH"]).all():
                        dates_eth.append(df.index[i+1])
                #if eth.iloc[i]["Close"] < eth.iloc[i]["200_day_MA"] and eth.iloc[i+14]["Close"] < eth.iloc[i+14]["200_day_MA"]:
                    #if eth.iloc[i+14]["Close"] > eth.iloc[i+14]["200_day_MA"]:
                        #dates.append(eth.index[i+14])
        if dates_eth:
          returns_eth = []
          for date in dates_eth:
              idx = df.index.get_loc(date)
              close_price = df.iloc[idx][f'price_{project_id}_eth']
    
              #if idx + 365 < len(df):
              return_data = {
                "date": date}
              if idx + 30 < len(df):
                return_data["30_day_return"] = (df.iloc[idx+30][f'price_{project_id}_eth'] - close_price) / close_price
              if idx + 45 < len(df): 
                return_data["45_day_return"] = (df.iloc[idx+45][f'price_{project_id}_eth'] - close_price) / close_price
              if idx + 60 < len(df): 
                return_data["60_day_return"] = (df.iloc[idx+60][f'price_{project_id}_eth'] - close_price) / close_price,
              if idx + 75 < len(df):    
                return_data["75_day_return"] = (df.iloc[idx+75][f'price_{project_id}_eth'] - close_price) / close_price,
              if idx + 90 < len(df):    
                return_data["90_day_return"] = (df.iloc[idx+90][f'price_{project_id}_eth'] - close_price) / close_price,
              if idx + 120 < len(df):    
                return_data["120_day_return"] = (df.iloc[idx+120][f'price_{project_id}_eth'] - close_price) / close_price,
              if idx + 150 < len(df):    
                return_data["150_day_return"] = (df.iloc[idx+150][f'price_{project_id}_eth'] - close_price) / close_price,
              if idx + 180 < len(df):    
                return_data["180_day_return"] = (df.iloc[idx+180][f'price_{project_id}_eth'] - close_price) / close_price,
              if idx + 365 < len(df):    
                return_data["365_day_return"] = (df.iloc[idx+365][f'price_{project_id}_eth'] - close_price) / close_pric,
                      
              returns_eth.append(return_data)  
          returns_eth = pd.DataFrame(returns_eth)
    
          average_returns_eth = {
          "30_day_return": (np.prod(1 + returns_eth["30_day_return"]) ** (1 / len(returns_eth["30_day_return"])) - 1) * 100,
          "45_day_return": (np.prod(1 + returns_eth["45_day_return"]) ** (1 / len(returns_eth["45_day_return"])) - 1) * 100,
          "60_day_return": (np.prod(1 + returns_eth["60_day_return"]) ** (1 / len(returns_eth["60_day_return"])) - 1) * 100,
          "75_day_return": (np.prod(1 + returns_eth["75_day_return"]) ** (1 / len(returns_eth["75_day_return"])) - 1) * 100,
          "90_day_return": (np.prod(1 + returns_eth["90_day_return"]) ** (1 / len(returns_eth["90_day_return"])) - 1) * 100,
          "120_day_return": (np.prod(1 + returns_eth["120_day_return"]) ** (1 / len(returns_eth["120_day_return"])) - 1) * 100,
          "150_day_return": (np.prod(1 + returns_eth["150_day_return"]) ** (1 / len(returns_eth["150_day_return"])) - 1) * 100,
          "180_day_return": (np.prod(1 + returns_eth["180_day_return"]) ** (1 / len(returns_eth["180_day_return"])) - 1) * 100,
          "365_day_return": (np.prod(1 + returns_eth["365_day_return"]) ** (1 / len(returns_eth["365_day_return"])) - 1) * 100
          }
    
          average_returns_eth = pd.Series(average_returns_eth)
    
        else:
          average_returns_eth = {}  # Empty dictionary if dates_eth is empty
    
        dates_btc = []
    
        for i in range(len(df) - 15):
            if df.iloc[i][f"{roll_2}_day_MA_BTC"] > df.iloc[i][f"{roll_1}_day_MA_BTC"]:
                if df.iloc[i+1][f"{roll_2}_day_MA_BTC"] < df.iloc[i+1][f"{roll_1}_day_MA_BTC"]:
                    if (df.iloc[i+1:i+16][f"{roll_2}_day_MA_BTC"] < df.iloc[i+1:i+16][f"{roll_1}_day_MA_BTC"]).all():
                        dates_btc.append(df.index[i+1])
                #if eth.iloc[i]["Close"] < eth.iloc[i]["200_day_MA"] and eth.iloc[i+14]["Close"] < eth.iloc[i+14]["200_day_MA"]:
                    #if eth.iloc[i+14]["Close"] > eth.iloc[i+14]["200_day_MA"]:
                        #dates.append(eth.index[i+14])
        if dates_btc:
          returns_btc = []
          for date in dates_btc:
              idx = df.index.get_loc(date)
              close_price = df.iloc[idx][f'price_{project_id}_btc']
    
              #if idx + 365 < len(df):
              return_data = {
                "date": date}
              if idx + 30 < len(df):
                return_data["30_day_return"] = (df.iloc[idx+30][f'price_{project_id}_btc'] - close_price) / close_price
              if idx + 45 < len(df): 
                return_data["45_day_return"] = (df.iloc[idx+45][f'price_{project_id}_btc'] - close_price) / close_price
              if idx + 60 < len(df): 
                return_data["60_day_return"] = (df.iloc[idx+60][f'price_{project_id}_btc'] - close_price) / close_price,
              if idx + 75 < len(df):    
                return_data["75_day_return"] = (df.iloc[idx+75][f'price_{project_id}_btc'] - close_price) / close_price,
              if idx + 90 < len(df):    
                return_data["90_day_return"] = (df.iloc[idx+90][f'price_{project_id}_btc'] - close_price) / close_price,
              if idx + 120 < len(df):    
                return_data["120_day_return"] = (df.iloc[idx+120][f'price_{project_id}_btc'] - close_price) / close_price,
              if idx + 150 < len(df):    
                return_data["150_day_return"] = (df.iloc[idx+150][f'price_{project_id}_btc'] - close_price) / close_price,
              if idx + 180 < len(df):    
                return_data["180_day_return"] = (df.iloc[idx+180][f'price_{project_id}_btc'] - close_price) / close_price,
              if idx + 365 < len(df):    
                return_data["365_day_return"] = (df.iloc[idx+365][f'price_{project_id}_btc'] - close_price) / close_pric,
                      
              returns_btc.append(return_data)  
          returns_btc = pd.DataFrame(returns_btc)
    
          average_returns_btc = {
              "30_day_return": (np.prod(1 + returns_btc["30_day_return"]) ** (1 / len(returns_btc["30_day_return"])) - 1) * 100,
              "45_day_return": (np.prod(1 + returns_btc["45_day_return"]) ** (1 / len(returns_btc["45_day_return"])) - 1) * 100,
              "60_day_return": (np.prod(1 + returns_btc["60_day_return"]) ** (1 / len(returns_btc["60_day_return"])) - 1) * 100,
              "75_day_return": (np.prod(1 + returns_btc["75_day_return"]) ** (1 / len(returns_btc["75_day_return"])) - 1) * 100,
              "90_day_return": (np.prod(1 + returns_btc["90_day_return"]) ** (1 / len(returns_btc["90_day_return"])) - 1) * 100,
              "120_day_return": (np.prod(1 + returns_btc["120_day_return"]) ** (1 / len(returns_btc["120_day_return"])) - 1) * 100,
              "150_day_return": (np.prod(1 + returns_btc["150_day_return"]) ** (1 / len(returns_btc["150_day_return"])) - 1) * 100,
              "180_day_return": (np.prod(1 + returns_btc["180_day_return"]) ** (1 / len(returns_btc["180_day_return"])) - 1) * 100,
              "365_day_return": (np.prod(1 + returns_btc["365_day_return"]) ** (1 / len(returns_btc["365_day_return"])) - 1) * 100
          }
    
          average_returns_btc = pd.Series(average_returns_btc)
        else:
          average_returns_btc = {}  # Empty dictionary if dates_eth is empty
    
        # Plot data
        fig, ax = plt.subplots(figsize=(20,8))
        ax.plot(df[f"price_{project_id}_usd"], label="Price in USD")
        ax.plot(df[f"{roll_1}_day_MA_USD"], label=f"{roll_1} day moving average")
        ax.plot(df[f"{roll_2}_day_MA_USD"], label=f"{roll_2} day moving average")
        # Add vertical lines for dates
        for date in dates_usd:
            ax.axvline(x=date, color='black', linestyle='--', alpha=0.9)
        # Add legend and title
        ax.legend(fontsize=16)
        ax.set_title(f"{project_id} Price and Moving Averages in USD", fontsize=16)
        ax.set_xlabel('Date', fontsize=16)
        ax.set_ylabel('Price', fontsize=16)
        # Plot data
        fig2, ax2 = plt.subplots(figsize=(20,8))
        ax2.plot(df[f"price_{project_id}_eth"], label="Price in ETH")
        ax2.plot(df[f"{roll_1}_day_MA_ETH"], label=f"{roll_1} day moving average")
        ax2.plot(df[f"{roll_2}_day_MA_ETH"], label=f"{roll_2} day moving average")
        # Add vertical lines for dates
        for date in dates_eth:
            ax2.axvline(x=date, color='black', linestyle='--', alpha=0.9)
        # Add legend and title
        ax2.legend(fontsize=16)
        ax2.set_title(f"{project_id} Price and Moving Averages in ETH", fontsize=16)
        ax2.set_xlabel('Date', fontsize=16)
        ax2.set_ylabel('Price', fontsize=16)
        # Plot data
        fig3, ax3 = plt.subplots(figsize=(20,8))
        ax3.plot(df[f"price_{project_id}_btc"], label="Price in BTC")
        ax3.plot(df[f"{roll_1}_day_MA_BTC"], label=f"{roll_1} day moving average")
        ax3.plot(df[f"{roll_2}_day_MA_BTC"], label=f"{roll_2} day moving average")
        # Add vertical lines for dates
        for date in dates_btc:
            ax3.axvline(x=date, color='black', linestyle='--', alpha=0.9)
        # Add legend and title
        ax3.legend(fontsize=16)
        ax3.set_title(f"{project_id} Price and Moving Averages in BTC", fontsize=16)
        ax3.set_xlabel('Date', fontsize=16)
        ax3.set_ylabel('Price', fontsize=16)
    
        if len(average_returns_usd) == 0:
            st.write(f'There is no crossing points for {project_id}-{roll_1} and {roll_2} in USD in given period')
        else:
          fig4, ax4 = plt.subplots(figsize=(20, 8))
          average_returns_usd.plot(kind='bar', color='crimson',label='Average returns', ax=ax4, fontsize=18)
          for i, v in enumerate(average_returns_usd.values):
            ax4.text(i, v + 0.02, f'{v:.2f}%', color='black', ha='center', fontsize=14)
          ax4.legend(loc='upper right', fontsize=18)
          ax4.set_title(f"Average returns after {project_id} {roll_1} days moving averages cross {roll_2} days moving averages line in USD", fontsize=18)
          ax4.set_xlabel("period", fontsize=18)
          ax4.set_ylabel("return", fontsize=18)
          plt.xticks(np.arange(9), ['30 days', '45 days', '60 days', '75 days', '90 days', '120 days', '150 days', '180 days', '365 days'])
        if len(average_returns_eth) == 0:
            st.write(f'There is no crossing points for {project_id}-{roll_1} and {roll_2} in ETH in given period')
        else:
          fig5, ax5 = plt.subplots(figsize=(20, 8))
          average_returns_eth.plot(kind='bar', color='crimson',label='Average returns', ax=ax5, fontsize=18)
          for i, v in enumerate(average_returns_eth.values):
            ax5.text(i, v + 0.02, f'{v:.2f}%', color='black', ha='center', fontsize=14)
          ax5.legend(loc='upper right', fontsize=18)
          ax5.set_title(f"Average returns after {project_id} {roll_1} days moving averages cross {roll_2} days moving averages line in ETH", fontsize=18)
          ax5.set_xlabel("period", fontsize=18)
          ax5.set_ylabel("return", fontsize=18)
          plt.xticks(np.arange(9), ['30 days', '45 days', '60 days', '75 days', '90 days', '120 days', '150 days', '180 days', '365 days'])
        if len(average_returns_btc) == 0:
          st.write(f'There is no crossing points for {project_id}-{roll_1} and {roll_2} in BTC in given period')
        else:
          fig6, ax6 = plt.subplots(figsize=(20, 8))
          average_returns_btc.plot(kind='bar', color='crimson',label='Average returns', ax=ax6, fontsize=18)
          for i, v in enumerate(average_returns_btc.values):
            ax6.text(i, v + 0.02, f'{v:.2f}%', color='black', ha='center', fontsize=14)
          ax6.legend(loc='upper right', fontsize=18)
          ax6.set_title(f"Average returns after {project_id} {roll_1} days moving averages cross {roll_2} days moving averages line in BTC", fontsize=18)
          ax6.set_xlabel("period", fontsize=18)
          ax6.set_ylabel("return", fontsize=18)
          plt.xticks(np.arange(9), ['30 days', '45 days', '60 days', '75 days', '90 days', '120 days', '150 days', '180 days', '365 days'])
        
        if len(average_returns_usd) == 0 and len(average_returns_eth) == 0 and len(average_returns_btc) == 0:
            return fig, fig2, fig3
        elif len(average_returns_usd) == 0 and len(average_returns_eth) == 0:
            return fig, fig2, fig3, fig6
        elif len(average_returns_usd) == 0 and len(average_returns_btc) == 0:
            return fig, fig2, fig3, fig5
        elif len(average_returns_eth) == 0 and len(average_returns_btc) == 0:
            return fig, fig2, fig3, fig4
        elif len(average_returns_usd) == 0:
            return fig, fig2, fig3, fig5, fig6
        elif len(average_returns_eth) == 0:
            return fig, fig2, fig3, fig4, fig6
        elif len(average_returns_btc) == 0:
            return fig, fig2, fig3, fig4, fig5
        else:
            return fig, fig2, fig3, fig4, fig5, fig6

    	
#with st.form("my_form",clear_on_submit=False):
    
project_id = st.text_input('Enter the project ID from Token Terminal', key='1')
ma1 = st.number_input('Enter the first number of days for moving averages', value=7, key='2')
ma2 = st.number_input('Enter the second number of days for moving averages', value=30, key='3')
date = st.date_input("Start Date", value=pd.to_datetime("2021-01-31", format="%Y-%m-%d"), key='4')

with st.form("monte_carlo_form"):
    if st.form_submit_button("Submit"):
        st.header(f"Here's Token price and {ma1}-days and {ma2}-days moving averages in USD with crossing points for {project_id.capitalize()}!")
        figures = plot_rolling_averages(project_id, ma1, ma2, date)
        
        st.pyplot(figures[0])
        st.header(f"Here's Token price and {ma1}-days and {ma2}-days moving averages in ETH with crossing points for {project_id.capitalize()}!")
        st.pyplot(figures[1])
        st.header(f"Here's Token price and {ma1}-days and {ma2}-days moving averages in BTC with crossing points for {project_id.capitalize()}!")
        st.pyplot(figures[2])

        if len(figures) > 3 and figures[3]:
            st.header(f"Here's Average returns after {project_id.capitalize()} {ma1} days moving averages cross {ma2} days moving averages line in USD!")
            st.pyplot(figures[3])
        if len(figures) > 4 and figures[4]:
            st.header(f"Here's Average returns after {project_id.capitalize()} {ma1} days moving averages cross {ma2} days moving averages line in ETH!")
            st.pyplot(figures[4])
        if len(figures) > 5 and figures[5]:
            st.header(f"Here's Average returns after {project_id.capitalize()} {ma1} days moving averages cross {ma2} days moving averages line in BTC!")
            st.pyplot(figures[5])
