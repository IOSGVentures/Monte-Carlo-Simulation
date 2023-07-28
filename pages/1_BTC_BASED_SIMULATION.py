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

st.set_page_config(page_title="MC Simulation using BTC IV", page_icon="🧐", layout="wide")
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
    st.title(":earth_asia: MC Simulation using BTC IV")
    st.markdown("##")
    def mcs_btc(project_id,sigma_btc,mean,price_levels):
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
        headers = {"Authorization": "Bearer 3365c8fd-ade3-410f-99e4-9c82d9831f0b"}
        response1 = requests.get(url1, headers=headers)
        data_shows1 = json.loads(response1.text)
        data1 = data_shows1['data']
        d1 = get_data(data1)
        d1 = d1[::-1]
        d1['Return'] = (np.log(d1['Price'])-np.log(d1['Price'].shift(1)))[1:]
        
        price_pr = d1['Return']
        realized_volatility_pr = np.std(price_pr[-365:]) * np.sqrt(365) * 100
        
        url3 = "https://api.tokenterminal.com/v2/projects/bitcoin/metrics?metric_ids=price"
        headers = {"Authorization": "Bearer 3365c8fd-ade3-410f-99e4-9c82d9831f0b"}
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
        
        headers = {"Authorization": "Bearer 3365c8fd-ade3-410f-99e4-9c82d9831f0b"}
        
        url = "https://api.tokenterminal.com/v2/projects/uniswap/metrics?metric_ids=price"
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
        sigma = sigma_btc+sigma_btc*dif
        mean = mean
        delta_t = 1/365
        num_periods = 365


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
            "Price Level": ["${0:,.1f}".format(price) for price in price_levels], # add $ and format prices
            "Probability": probabilities
        })
        table.insert(0, "Current Price", "${0:,.2f}".format(price0))
        table["Probability"] = table["Probability"].apply(lambda x: f"{x:.2%}")
        fig, ax = plt.subplots(figsize=(30,12))

        ax.plot(result)
        ax.set_title(f'Monte Carlo Simulation {project_id} price 1 year from now')
        print(table.to_string(index=False))
        return table.to_string(index=False),fig
    with st.form("my_form"):
        project_id = st.text_input('Enter the project ID from Token Terminal',key='1')
        sigma_btc = float(st.text_input('Enter the sigma-implied volatility from in the money option -  deribit',key='2'))
        mean = float(st.text_input('Enter the mean-risk-neutral assumption underpinning option pricing models',key='3'))
        price_levels = list(st.text_input('Enter the price levels',key='4'))
        period = int(st.text_input('Enter the number of days',key='5'))
        
        submitted = st.form_submit_button("Submit")
    
        if submitted:
            st.header(f"Here's Monte Carlo Simulation for {project_id.capitalize()}!")
            table, f = mcs_btc(project_id,sigma_btc,mean,price_levels)
            st.dataframe(table, use_container_width=True)
            st.pyplot(f)
            
