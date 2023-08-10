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

st.set_page_config(page_title="MC Simulation using ETH IV", page_icon="🧐", layout="wide")
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
    st.title(":earth_asia: MC Simulation using ETH IV")
    st.markdown("##")
    def mcs_eth_2(project_id,sigma_eth,mean,period_in_days):
      def get_data(data):
          date = []
          price = []
          for i in range(len(data)):
              date.append(pd.to_datetime((data[i]['timestamp'])))
              price.append(data[i]['price'])
          dataa = [price]
          df = pd.DataFrame(dataa, columns=date, index=['Price'])
          df = df.T.dropna()
          return df
    
      url1 = f"https://api.tokenterminal.com/v2/projects/{project_id}/metrics?metric_ids=price"
      headers = {"Authorization": st.secrets["Authorization"]}
      response1 = requests.get(url1, headers=headers)
      data_shows1 = json.loads(response1.text)
      data1 = data_shows1['data']
      d1 = get_data(data1)
      d1 = d1[::-1]
      d1['Return'] = (np.log(d1['Price'])-np.log(d1['Price'].shift(1)))[1:]
    
      price_pr = d1['Return']
      realized_volatility_pr = np.std(price_pr[-365:]) * np.sqrt(365) * 100
    
      url3 = "https://api.tokenterminal.com/v2/projects/ethereum/metrics?metric_ids=price"
      headers = {"Authorization": st.secrets["Authorization"]}
      response3 = requests.get(url3, headers=headers)
      data_shows3 = json.loads(response3.text)
      data3 = data_shows3['data']
      d3 = get_data(data3)
      d3 = d3[::-1]
      d3['Return'] = (np.log(d3['Price'])-np.log(d3['Price'].shift(1)))[1:]
    
      price_btc = d3['Return']
      realized_volatility_btc = np.std(price_btc[-365:]) * np.sqrt(365) * 100
    
      pr_btc = realized_volatility_pr/realized_volatility_btc
      dif = pr_btc-1
    
    
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
    
      headers = {"Authorization": st.secrets["Authorization"]}
    
      url = f"https://api.tokenterminal.com/v2/projects/{project_id}/metrics?metric_ids=price"
      response = requests.get(url, headers=headers)
      data_shows = json.loads(response.text)
      data = data_shows['data']
      ens = get_data(data)
      ens = ens[::-1]
      ens_lr = (np.log(ens)-np.log(ens.shift(1)))[1:].dropna()
    
      ens_std = np.std(ens_lr)[0] * np.sqrt(365)
      ens_daily_mean = ens_lr.mean()[0]
      ens_mean = (1+ens_daily_mean)**365-1
      price0 = ens[-1:]['price'][0]
      sigma = sigma_eth+sigma_eth*dif
      mean = mean
      delta_t = 1/365
      num_periods = period_in_days
      price_levels = [
            float(round((price0 - 0.9 * price0),4)),  # current_price - 90%
            float(round((price0 - 0.85 * price0),4)),  # current_price - 90%
            float(round((price0 - 0.8 * price0),4)),  # current_price - 90%
            float(round((price0 - 0.75 * price0),4)),  # current_price - 90%
            float(round((price0 - 0.7 * price0),4)),  # current_price - 70%
            float(round((price0 - 0.65 * price0),4)),  # current_price - 60%
            float(round((price0 - 0.6 * price0),4)),  # current_price - 60%
            float(round((price0 - 0.55 * price0),4)),  # current_price - 50%
            float(round((price0 - 0.5 * price0),4)),  # current_price - 50%
            float(round((price0 - 0.45 * price0),4)),  # current_price - 40%
            float(round((price0 - 0.4 * price0),4)),  # current_price - 40%
            float(round((price0 - 0.35 * price0),4)),  # current_price - 30%
            float(round((price0 - 0.32 * price0),4)),  # current_price - 30%
            float(round((price0 - 0.3 * price0),4)),  # current_price - 30%
            float(round((price0 - 0.27 * price0),4)),  # current_price - 20%
            float(round((price0 - 0.25 * price0),4)),  # current_price - 20%
            float(round((price0 - 0.22 * price0),4)),  # current_price - 20%
            float(round((price0 - 0.2 * price0),4)),  # current_price - 20%
            float(round((price0 - 0.18 * price0),4)),  # current_price - 20%
            float(round((price0 - 0.15 * price0),4)),  # current_price - 20%
            float(round((price0 - 0.12 * price0),4)),  # current_price - 20%
            float(round((price0 - 0.1 * price0),4)),  # current_price - 20%
            float(round((price0 - 0.08 * price0),4)),  # current_price - 20%
            float(round((price0 - 0.05 * price0),4)),  # current_price - 20%
            float(round((price0 - 0.002 * price0),4)),  # current_price - 20%
            float(round((price0),4)),                 # current_price
            float(round((price0 + 0.02 * price0),4)),  # current_price - 20%
            float(round((price0 + 0.05 * price0),4)),  # current_price - 20%
            float(round((price0 + 0.07 * price0),4)),  # current_price - 20%
            float(round((price0 + 0.1 * price0),4)),  # current_price - 20%
            float(round((price0 + 0.12 * price0),4)),  # current_price - 20%
            float(round((price0 + 0.15 * price0),4)),  # current_price - 20%
            float(round((price0 + 0.17 * price0),4)),  # current_price - 20%
            float(round((price0 + 0.2 * price0),4)),  # current_price + 20%
            float(round((price0 + 0.22 * price0),4)),  # current_price + 20%
            float(round((price0 + 0.25 * price0),4)),  # current_price + 20%
            float(round((price0 + 0.27 * price0),4)),  # current_price + 20%
            float(round((price0 + 0.3 * price0),4)),  # current_price + 20%
            float(round((price0 + 0.32 * price0),4)),  # current_price + 20%
            float(round((price0 + 0.35 * price0),4)),  # current_price + 20%
            float(round((price0 + 0.37 * price0),4)),   # current_price + 40%
            float(round((price0 + 0.4 * price0),4)),  # current_price + 60%
            float(round((price0 + 0.42 * price0),4)),  # current_price + 80%
            float(round((price0 + 0.5 * price0),4)),   # current_price + 200%
            float(round((price0 + 0.7 * price0),4)),   # current_price + 300%
            float(round((price0 + 0.9 * price0),4)),   # current_price + 400%
            float(round((price0 + price0),4)),   # current_price + 600%
            float(round((price0 + 2.5 * price0),4)),   # current_price + 1000%
            float(round((price0 + 3 * price0),4)),   # current_price + 1500%
            float(round((price0 + 4 * price0),4)),  # current_price + 1500%
            float(round((price0 + 5 * price0),4)),   # current_price + 1500%
            float(round((price0 + 6 * price0),4)),   # current_price + 1500%
            float(round((price0 + 7 * price0),4)),   # current_price + 1500%
            float(round((price0 + 8 * price0),4)),   # current_price + 1500%
            float(round((price0 + 9 * price0),4)),   # current_price + 1500%
            float(round((price0 + 10 * price0),4))   # current_price + 1500%
        ]
    
      def model(price0=price0, sigma=sigma, mean=mean, delta_t=delta_t, num_periods=num_periods):
    
          price_estimate = [price0]
          for i in range(num_periods):
              price_estimate.append(price_estimate[i] * np.exp((mean - sigma**2/2)*delta_t + sigma * np.random.normal(0, 1) * np.sqrt(delta_t)))
    
          return price_estimate
    
      def MonteCarlo(simulation_number = 10000):
    
          prices = {}
    
          for i in range(simulation_number):
              prices[i] = pd.DataFrame(model(), columns=[i])
    
          return pd.concat([prices[i] for i in range(len(prices))], axis=1)
    
      def count_simulations(result, price_level, price0):
          if price_level < price0:
              return (result <= price_level).any(axis=0).sum()
          else:
              return (result >= price_level).any(axis=0).sum()
    
    
      result = MonteCarlo()
    
      price_levels = price_levels
    
      probabilities = []
      for price_level in price_levels:
          num_simulations = count_simulations(result, price_level, price0)
          prob = num_simulations / result.shape[1]
          probabilities.append(prob)
    
      # Create a table of current price and probabilities
      table = pd.DataFrame({
          "Price Level": ["${0:,.4f}".format(price) for price in price_levels], # add $ and format prices
          "Probability": probabilities
      })
      table.insert(0, "Current Price", "${0:,.4f}".format(price0))
      table["Probability"] = table["Probability"].apply(lambda x: f"{x:.2%}")
      fig, ax = plt.subplots(figsize=(30,12))
    
      ax.plot(result)
      ax.set_title(f'Monte Carlo Simulation {project_id} price {period_in_days} days from now')
      #st.write(table.to_string(index=False))
      return table,fig
#with st.form("my_form",clear_on_submit=False):
    
project_id = st.text_input('Enter the project ID from Token Terminal', key='1')
sigma_btc = st.number_input('Enter the sigma-implied volatility from in the money option - deribit', key='2', value=0.5)
mean = st.number_input('Enter the mean-risk-neutral assumption underpinning option pricing models', key='3', value=0.05)
period = st.number_input('Enter the number of days', key='4', value=365)
# Wrap the code within an st.form() block
with st.form("monte_carlo_form"):
    if st.form_submit_button("Submit"):
        st.header(f"Here's Monte Carlo Simulation for {project_id.capitalize()}!")
        table, f = mcs_eth_2(project_id, sigma_btc, mean, period)

        if not isinstance(table, pd.DataFrame):
            st.error("Error: The 'table' variable is not a pandas DataFrame.")
        else:
            st.dataframe(table, use_container_width=True)
            st.pyplot(f)
            
