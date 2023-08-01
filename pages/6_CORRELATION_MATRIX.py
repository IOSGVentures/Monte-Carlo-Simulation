import numpy as np
import altair as alt
import pandas as pd
import streamlit as st
import requests
import json
import seaborn as sns
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
    st.title(":earth_asia: Correlation between token parameters")
    st.markdown("##")
    def get_correlation_matrix(project_id, num_days):
        url = f"https://api.tokenterminal.com/v2/projects/{project_id}/metrics"
        headers = {"Authorization": "Bearer 3365c8fd-ade3-410f-99e4-9c82d9831f0b"}
        response = requests.get(url, headers=headers)
        data_shows = json.loads(response.text)
        data = data_shows['data']
        def get_data_price(data):
          date = []
          price = []
          market_cap_fully_diluted = []
          token_trading_volume = []
          tokenholders = []
          net_deposits = []
          tvl = []
          trading_volume = []
          fees = []
          treasury = []
          treasury_net = []
          user_dau = []
          user_wau = []
          user_mau = []
          active_developers = []
          code_commits = []
    
          for i in range(len(data)):
              date.append(pd.to_datetime((data[i]['timestamp'])))
              price.append(data[i]['price'])
              market_cap_fully_diluted.append(data[i]['market_cap_fully_diluted'])
              token_trading_volume.append(data[i]['token_trading_volume'])
              tokenholders.append(data[i]['tokenholders'])
              net_deposits.append(data[i]['net_deposits'])
              tvl.append(data[i]['tvl'])
              trading_volume.append(data[i]['trading_volume'])
              fees.append(data[i]['fees'])
              treasury.append(data[i]['treasury'])
              treasury_net.append(data[i]['treasury_net'])
              user_dau.append(data[i]['user_dau'])
              user_wau.append(data[i]['user_wau'])
              user_mau.append(data[i]['user_mau'])
              active_developers.append(data[i]['active_developers'])
              code_commits.append(data[i]['code_commits'])
          dataa = [price,market_cap_fully_diluted,token_trading_volume,tokenholders,net_deposits,tvl,trading_volume,fees,treasury,treasury_net,user_dau,user_wau,user_mau,active_developers,code_commits]
          df = pd.DataFrame(dataa, columns=date, index=['price','market_cap_fully_diluted','token_trading_volume','tokenholders','net_deposits','tvl','trading_volume','fees','treasury','treasury_net','user_dau','user_wau','user_mau','active_developers','code_commits'])
          df = df.T.dropna()
          return df
        d = get_data_price(data)
        d = d[::-1]
        d.index = pd.to_datetime(d.index).tz_localize(None)
        d_selected = d.tail(num_days)
    
        # Assuming your DataFrame is called "df"
        correlation_matrix = d_selected.corr()
    
        # Create a heatmap
        fig = plt.figure(figsize=(14, 10))
        sns.heatmap(correlation_matrix, annot=True, cmap="RdYlBu")
        plt.title('Correlation Matrix')
                    
        # Display the plot
        return fig

    	
#with st.form("my_form",clear_on_submit=False):
    
project_id = st.text_input('Enter the project ID from Token Terminal', key='1')
date = st.number_input("Number of days for calculation", value=365)

with st.form("monte_carlo_form"):
    if st.form_submit_button("Submit"):
        st.header(f"Here's Correlation matrix between different parameters for {project_id.capitalize()}!")
        f1 = get_correlation_matrix(project_id, date)
        
        st.pyplot(f1)
