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
    st.title(":earth_asia: Correlation between token parameters timeseries")
    st.markdown("##")
    def plot_rolling_correlation(project_id, param1, param2,start_date):
      def get_data_price(data):
        date = []
        price = []
        market_cap_fully_diluted = []
        token_trading_volume = []
        tokenholders = []
        
        tvl = []
        trading_volume = []
        fees = []
        
      
        user_wau = []
     
        active_developers = []
        code_commits = []
    
        for i in range(len(data)):
            date.append(pd.to_datetime((data[i]['timestamp'])))
            price.append(data[i]['price'])
            market_cap_fully_diluted.append(data[i]['market_cap_fully_diluted'])
            token_trading_volume.append(data[i]['token_trading_volume'])
            tokenholders.append(data[i]['tokenholders'])
            
            tvl.append(data[i]['tvl'])
            trading_volume.append(data[i]['trading_volume'])
            fees.append(data[i]['fees'])
            
           
            user_wau.append(data[i]['user_wau'])
       
            active_developers.append(data[i]['active_developers'])
            code_commits.append(data[i]['code_commits'])
        dataa = [price,market_cap_fully_diluted,token_trading_volume,tokenholders,tvl,trading_volume,fees,user_wau,active_developers,code_commits]
        df = pd.DataFrame(dataa, columns=date, index=['price','market_cap_fully_diluted','token_trading_volume','tokenholders','tvl','trading_volume','fees','user_wau','active_developers','code_commits'])
        df = df.T.dropna()
        return df
      url = f"https://api.tokenterminal.com/v2/projects/{project_id}/metrics"
      headers = {"Authorization": "Bearer 3365c8fd-ade3-410f-99e4-9c82d9831f0b"}
      response = requests.get(url, headers=headers)
      data_shows = json.loads(response.text)
      data = data_shows['data']
      d = get_data_price(data)
      d = d[::-1]
      d = d[f'{start_date}':]
      d.index = pd.to_datetime(d.index).tz_localize(None)
      # Calculate the correlation matrix between all parameters
      correlation_matrix = d.corr()

      # Calculate rolling 30-day correlation between the two specified parameters
      rolling_correlation = d[param1].rolling(window=30).corr(d[param2])

      # Create a line chart
      f = plt.figure(figsize=(14, 8))
      plt.plot(d.index, rolling_correlation, color='blue')
      plt.xlabel('Date')
      plt.ylabel('Rolling 30-Day Correlation')
      plt.title(f'Rolling 30-Day Correlation between {param1} and {param2}')
      plt.xticks(rotation=45)
      plt.grid(True)

      # Display the plot
      plt.show()
      return f
#with st.form("my_form",clear_on_submit=False):
    
project_id = st.text_input('Enter the project ID from Token Terminal', key='1')

# Define the parameter options
parameter_options = [
    "price",
    "market_cap_fully_diluted",
    "token_trading_volume",
    "tokenholders",
    "tvl",
    "trading_volume",
    "fees",
    "user_wau",
    "active_developers",
    "code_commits"
]

# Create checkboxes for the parameters
par1 = st.checkbox("Price", key='2')
par2 = st.checkbox("FDV", key='3')
par3 = st.checkbox("Token trading volume", key='4')
par4 = st.checkbox("Tokenholders", key='5')
par5 = st.checkbox("TVL", key='6')
par6 = st.checkbox("Trading volume", key='7')
par7 = st.checkbox("Fees", key='8')
par8 = st.checkbox("Weekly active users", key='9')
par9 = st.checkbox("Active developers", key='10')
par10 = st.checkbox("Code commits", key='11')
start_date = st.date_input("Start date", key='12')

with st.form("monte_carlo_form"):
    if st.form_submit_button("Submit"):
        # Get the selected parameters
        selected_parameters = [parameter_options[i] for i, param in enumerate([par1, par2]) if param]
        
        # Check if at least one parameter is selected
        if not selected_parameters:
            st.error("Please select at least one parameter.")
        else:
            # Now you can use the selected_parameters list in your function plot_rolling_correlation()
            # For example: plot_rolling_correlation(project_id, selected_parameters[0], selected_parameters[1])
            st.header(f"Here's Correlation timeseries between {selected_parameters[0]} and {selected_parameters[1]} for {project_id.capitalize()}!")
            f = plot_rolling_correlation(project_id, selected_parameters[0], selected_parameters[1])
            st.pyplot(f)

