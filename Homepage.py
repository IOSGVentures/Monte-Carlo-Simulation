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

st.set_page_config(page_title="Token Vesting Management Homepage", page_icon="🧐", layout="wide")
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
    authenticator.logout('Logout', 'main', key='unique_key')
    st.write(f'Welcome *{name}*')
    
    # ---- SIDEBAR ----
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success("Choose page above")
    
    
    # ---- MAINPAGE ----
    st.title(":bar_chart: Token Vesting Management Homepage")
    st.markdown("##")
    st.write('
Welcome to IOSG token vesting management web application!

At this Application, we have a way to easily manage our acquired tokens. Our intuitive and user-friendly platform empowers you to effortlessly oversee all our invested projects in one centralized location, providing you with key parameters at your fingertips.

With our first page dedicated to displaying comprehensive information about all our invested projects, you can easily keep track of important details such as project names, token quantities, vesting periods, ROI and much more. This overview ensures that you have a clear understanding of our token allocation, enabling you to make informed decisions and effectively manage our portfolio.

Second page is designed specifically for token vesting. This page allows you to efficiently handle the process for the upcoming month.')
    
