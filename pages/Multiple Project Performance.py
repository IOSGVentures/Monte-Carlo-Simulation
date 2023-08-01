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
    st.title(":earth_asia: Multiple project performance timeseries")
    st.markdown("##")
    def multiple_projects_performance(project_ids, start_date, entry_money):

    """
    This function takes a list of project ids, a start date and an entry investment amount as input.
    It uses the Token Terminal API to retrieve historical price data for each project and calculates
    the relative performance of the entry investment amount over time for each project.
    The function returns a plot of the relative performance of the entry investment amount in each project.

    Args:
    - project_ids: list - a list of project ids for which to retrieve price data
    - start_date: str - the start date of the analysis in 'YYYY-MM-DD' format
    - entry_money: float - the amount of money to invest initially in each project

    Returns:
    - matplotlib.figure.Figure - a plot of the relative performance of the entry investment amount in each project

     Example usage:

        from multiple_projects_performance import multiple_projects_performance
        project_ids = ['bitcoin', 'ethereum']
        start_date = '2022-01-01'
        result = multiple_projects_performance(project_ids, start_date)
    """
      start_date = pd.to_datetime(start_date)
      def standardize(data, start_value):
          data.iloc[0] = start_value

          for i in range(1, len(data)):
              data.iloc[i] = data.iloc[i-1] * np.exp(data.iloc[i])

          return data

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

      d_list = []
      for project_id in project_ids:
          url = f"https://api.tokenterminal.com/v2/projects/{project_id}/metrics?metric_ids=price"
          response = requests.get(url, headers=headers)
          data_shows = json.loads(response.text)
          data = data_shows['data']
          d = get_data(data)
          d = d[::-1]
          d_CCR = (np.log(d)-np.log(d.shift(1)))[1:]
          #d_CCR = d_CCR.iloc[::-1]
          d_stand = standardize(d_CCR['price'][((d_CCR.index.year >= start_date.year) & (d_CCR.index.month >= start_date.month) & (d_CCR.index.day >= start_date.day)) | (d_CCR.index.year > start_date.year)], start_value=entry_money)
          d_list.append(d_stand)

      stand = pd.concat(d_list, axis=1, keys=project_ids)

      fig, ax = plt.subplots(figsize=(14, 8))
      stand.plot(ax=ax)

      ax.set_title(f"Relative performance of ${entry_money} invested in {len(project_ids)} projects at {start_date}", fontsize=18)
      ax.set_xlabel('Date', fontsize=18)
      ax.set_ylabel('Balance', fontsize=18)
      return fig

    	
#with st.form("my_form",clear_on_submit=False):
    
project_ids = st.text_input('Enter the project ID from Token Terminal', key='1')
date = st.date_input("Start Date", value=pd.to_datetime("2021-01-31", format="%Y-%m-%d"))
money = st.number_input("Entry money", value=1000)
project_ids_list = project_ids.split(",")  
with st.form("monte_carlo_form"):
    if st.form_submit_button("Submit"):
        st.header(f"Here's Timeseries with token price in USD, ETH and BTC for {project_id.capitalize()}!")
        f1 = multiple_projects_performance(project_ids, date, money)
        
        st.pyplot(f1)