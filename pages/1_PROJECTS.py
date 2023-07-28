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
    

    columns = 3  # Number of columns
    selected_projects = []

    with st.form('checkbox_form'):
        st.write('Which project would you like to check?')

        # List of checkbox labels
        checkbox_labels = [
            'Illuvium','Arweave', 'Synthetix','Automata', 'Liquity',
            'Coin98','Uma', 'Mcdex', 'Izumi', 'Insurace', 'Thales',
            'Impossible finance', 'Moonbeam', 'Astar', 'uJenny',
            'Finnexus', 'Stakewise', 'Centrifuge',
            'Galaxy', 'Kyve network', 'Mina','Meta pool', 'Cypher MOD',
            'Starkware', 'Aurora', 'Daosquare', 'Burrow', 'Gitcoin', 'Treasure DAO', 'Alethea', 'Perion'
        ]

        # Calculate the number of rows
        num_rows = len(checkbox_labels) // columns + 1

        for i in range(num_rows):
            cols_container = st.columns(columns)

            for j in range(columns):
                index = i * columns + j

                if index < len(checkbox_labels):
                    # Store the checkbox value in a variable
                    checkbox_value = cols_container[j].checkbox(
                        label=checkbox_labels[index], key=index
                    )

                    # Add the selected project to the list
                    if checkbox_value:
                        selected_projects.append(checkbox_labels[index])
        submitted = st.form_submit_button('Submit')
    
    #if submitted:
        # Display charts for selected projects
        for project in selected_projects:

            st.header(f"Here's Token Vesting Schedule for {project.capitalize()}!")
            if project=='Illuvium':
                df_ilv, f, f2 = ilv()
                current_token_amount = df_ilv['current_token_amount'].iloc[-1]
                current_roi = df_ilv['current_roi'].iloc[-1]
                current_usd_amount = df_ilv['current_usd_amount'].iloc[-1]
                next_vesting_date = df_ilv['next_vesting_date'].iloc[-1]
                end_of_vesting = df_ilv['end_of_vesting'].iloc[-1].date()
                unlocked_pct_tokens = df_ilv['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} ILV")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                col4.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Arweave':
                df_ar,f, f2 = ar()
                current_token_amount = df_ar['current_token_amount'].iloc[-1]
                current_roi = df_ar['current_roi'].iloc[-1]
                current_usd_amount = df_ar['current_usd_amount'].iloc[-1]
                unlocked_pct_tokens = df_ar['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} AR")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                col4.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f2)
            if project=='Synthetix':
                d,f,f2 = snx()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} SNX")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                col4.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f2)
            if project=='Automata':
                d1,f1,f11 = ata1()
                d2,f2,f22 = ata2()
                current_token_amount = d1['current_token_amount'].iloc[-1]
                current_roi = d1['current_roi'].iloc[-1]
                current_usd_amount = d1['current_usd_amount'].iloc[-1]
                unlocked_pct_tokens = d1['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} ATA")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                col4.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f1)
                st.pyplot(f11)
                
                current_token_amount = d2['current_token_amount'].iloc[-1]
                current_roi = d2['current_roi'].iloc[-1]
                current_usd_amount = d2['current_usd_amount'].iloc[-1]
                unlocked_pct_tokens = d2['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} ATA")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                col4.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f2)
                st.pyplot(f22)
            if project=='Liquity':
                d,f,f2 = lqty()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} LQTY")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                end_of_vesting = d['end_of_vesting'].iloc[-1].date()
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Next vesting date**", f"{next_vesting_date}")
                col2.metric("**End of vesting**", f"{end_of_vesting} ")
                col3.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Coin98':
                d,f,f2 = c98()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} C98")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                end_of_vesting = d['end_of_vesting'].iloc[-1].date()
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Next vesting date**", f"{next_vesting_date}")
                col2.metric("**End of vesting**", f"{end_of_vesting} ")
                col3.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Uma':
                d,f,f2 = uma()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} UMA")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                col4.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f2)
            if project=='Mcdex':
                d,f,f2 = mux()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} MUX")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                col4.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f2)
            if project=='Insurace':
                d,f,f2 = insur()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} INSUR")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                col4.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f2)
            if project=='Izumi':
                d,f,f2 = izi()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                end_of_vesting = d['end_of_vesting'].iloc[-1].date()
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} IZI")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                col4.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f2)
            if project=='Thales':
                d,f,f2 = thales()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} THALES")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                end_of_vesting = d['end_of_vesting'].iloc[-1].date()
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Next vesting date**", f"{next_vesting_date}")
                col2.metric("**End of vesting**", f"{end_of_vesting} ")
                col3.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Impossible finance':
                d,f,f2 = imf()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} IF")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                col4.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f2)
            if project=='Moonbeam':
                d,f,f2 = glmr()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} GLMR")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                col4.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f2)
            if project=='Astar':
                d,f,f2 = astr()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} ASTR")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                col4.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f2)
            if project=='uJenny':
                d,f,f2 = ujenny()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} UJENNY")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                col4.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f2)
            if project=='Finnexus':
                d,f = fnx()
                current_token_amount = d['current_token_amount'].iloc[-1]
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2 = st.columns(2)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} FNX")
                col2.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
            if project=='Stakewise':
                d,f,f2 = swise()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} SWISE")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                end_of_vesting = d['end_of_vesting'].iloc[-1].date()
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Next vesting date**", f"{next_vesting_date}")
                col2.metric("**End of vesting**", f"{end_of_vesting} ")
                col3.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Centrifuge':
                d,f,f2 = cfg()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} CFG")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                end_of_vesting = d['end_of_vesting'].iloc[-1].date()
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Next vesting date**", f"{next_vesting_date}")
                col2.metric("**End of vesting**", f"{end_of_vesting} ")
                col3.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Galaxy':
                d,f,f2 = gxy()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} GAL")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                end_of_vesting = d['end_of_vesting'].iloc[-1].date()
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Next vesting date**", f"{next_vesting_date}")
                col2.metric("**End of vesting**", f"{end_of_vesting} ")
                col3.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Kyve network':
                d,f,f2 = kyve()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} KYVE")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                end_of_vesting = d['end_of_vesting'].iloc[-1].date()
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Next vesting date**", f"{next_vesting_date}")
                col2.metric("**End of vesting**", f"{end_of_vesting} ")
                col3.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f)
                st.pyplot(f2) 
            if project=='Mina':
                d,f,f2 = mina()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} MINA")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                end_of_vesting = d['end_of_vesting'].iloc[-1].date()
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Next vesting date**", f"{next_vesting_date}")
                col2.metric("**End of vesting**", f"{end_of_vesting} ")
                col3.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Meta pool':
                d,f,f2 = meta()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} META")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                end_of_vesting = d['end_of_vesting'].iloc[-1].date()
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Next vesting date**", f"{next_vesting_date}")
                col2.metric("**End of vesting**", f"{end_of_vesting} ")
                col3.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Cypher MOD':
                d,f,f2 = cpr()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} CPR")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                end_of_vesting = d['end_of_vesting'].iloc[-1].date()
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Next vesting date**", f"{next_vesting_date}")
                col2.metric("**End of vesting**", f"{end_of_vesting} ")
                col3.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Starkware':  
                d,f = stark()
                current_token_amount = d['current_token_amount'].iloc[-1]
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                end_of_vesting = d['end_of_vesting'].iloc[-1].date()
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} STRK")
                col2.metric("**Next vesting date**", f"{next_vesting_date}")
                col3.metric("**End of vesting**", f"{end_of_vesting}")
                col4.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f)
            if project=='Aurora':
                d,f,f2 = aurora()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} AURORA")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                end_of_vesting = d['end_of_vesting'].iloc[-1].date()
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Next vesting date**", f"{next_vesting_date}")
                col2.metric("**End of vesting**", f"{end_of_vesting} ")
                col3.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Daosquare':
                d,f,f2 = rice()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} RICE")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                end_of_vesting = d['end_of_vesting'].iloc[-1].date()
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Next vesting date**", f"{next_vesting_date}")
                col2.metric("**End of vesting**", f"{end_of_vesting} ")
                col3.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Burrow':
                d,f,f2 = brrr()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} BRRR")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                end_of_vesting = d['end_of_vesting'].iloc[-1].date()
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Next vesting date**", f"{next_vesting_date}")
                col2.metric("**End of vesting**", f"{end_of_vesting} ")
                col3.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Gitcoin':
                d,f,f2 = gtc()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} GTC")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                end_of_vesting = d['end_of_vesting'].iloc[-1].date()
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Next vesting date**", f"{next_vesting_date}")
                col2.metric("**End of vesting**", f"{end_of_vesting} ")
                col3.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Treasure DAO':
                d,f,f2 = magic()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} MAGIC")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                end_of_vesting = d['end_of_vesting'].iloc[-1].date()
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Next vesting date**", f"{next_vesting_date}")
                col2.metric("**End of vesting**", f"{end_of_vesting} ")
                col3.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Alethea':
                d,f,f2 = ali()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} ALI")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                end_of_vesting = d['end_of_vesting'].iloc[-1].date()
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Next vesting date**", f"{next_vesting_date}")
                col2.metric("**End of vesting**", f"{end_of_vesting} ")
                col3.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Perion':
                d,f,f2 = perc()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Token Amount**", f"{numerize(current_token_amount)} PERC")
                col2.metric("**ROI**", f"{current_roi} %")
                col3.metric("**USD amount**", f"{numerize(current_usd_amount)} $")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                end_of_vesting = d['end_of_vesting'].iloc[-1].date()
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                col1, col2, col3 = st.columns(3)
                col1.metric("**Next vesting date**", f"{next_vesting_date}")
                col2.metric("**End of vesting**", f"{end_of_vesting} ")
                col3.metric("**Unlocked**", f"{numerize(unlocked_pct_tokens)} %")
                st.pyplot(f)
                st.pyplot(f2)
