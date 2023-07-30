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

st.set_page_config(page_title="Monte Carlo Simulation", page_icon="🧐", layout="wide")
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
    st.sidebar.success("Choose page above")
    authenticator.logout("Logout", "sidebar")
    
    # ---- MAINPAGE ----
    st.title(":bar_chart: Monte Carlo Simulation")
    st.markdown("##")
    st.write('Welcome to Monte Carlo Simulation web application!')
    st.write('At this Application, We can easily simulate the price movement of any token in an arbitrary time frame.')
    st.write('And we can calculate the probability that the price of that token will be at a certain level in the selected time frame.')
    st.write('We use Geometric Brownian Motion (assumption of the Black-Scholes model) and Monte Carlo simulation to obtain probabilities.')
    st.write('Parameters that were used for the simulation')

    st.write('sigma (implied volatility from in the money option - (https://www.deribit.com/options/ETH)')
    st.write('mean (here we leverage risk-neutral assumption underpinning option pricing models - (https://ycharts.com/indicators/1_year_treasury_rate)')
    st.write('period (default - one year from now)')
    
