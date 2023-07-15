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

st.set_page_config(page_title="Invested Projects Overview", page_icon="🧐", layout="wide")
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
    st.title(":earth_asia: Invested Projects Overview")
    st.markdown("##")
    
    def ilv():
        token_ticker = "ILV"
        coingecko_id = "illuvium"
        entry_price = 3
        vesting_schedule = {pd.Timestamp('2022-07-30'):8.33, pd.Timestamp('2022-08-30'):8.33, pd.Timestamp('2022-09-30'):8.33, pd.Timestamp('2022-10-30'):8.33,
                            pd.Timestamp('2022-11-30'):8.33, pd.Timestamp('2022-12-30'):8.33,pd.Timestamp('2023-01-30'):8.33,
                            pd.Timestamp('2023-02-28'):8.33,pd.Timestamp('2023-03-30'):8.34,pd.Timestamp('2023-04-30'):8.34,pd.Timestamp('2023-05-30'):8.34,pd.Timestamp('2023-06-30'):8.34}
        tge_date = "2022-01-01"
        total_tokens_number = 66666.67 

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)


        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_ilv = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_ilv.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_ilv.loc[date, 'current_roi'] = round(current_roi, 2)
            df_ilv.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_ilv.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_ilv.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_ilv.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_ilv.index = df_ilv.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_ilv['next_vesting_date'] = df_ilv['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_ilv = df_ilv.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_ilv.rename(columns={'price': 'token_price'}, inplace=True)
        df_ilv['ROI'] = (df_ilv['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_ilv.index, df_ilv['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_ilv.index, df_ilv['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        return df_ilv,fig,fig2

    def ar():
        token_ticker = "AR"
        coingecko_id = "arweave"
        entry_price = 4.63
        vesting_schedule = {pd.Timestamp('2022-02-02'):100}
        tge_date = "2019-11-01"
        total_tokens_number = 250000

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)


        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_ar = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_ar.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_ar.loc[date, 'current_roi'] = round(current_roi, 2)
            df_ar.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_ar.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_ar.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_ar.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_ar.index = df_ar.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_ar['next_vesting_date'] = df_ar['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_ar = df_ar.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_ar.rename(columns={'price': 'token_price'}, inplace=True)
        df_ar['ROI'] = (df_ar['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_ar.index, df_ar['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_ar.index, df_ar['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        return df_ar,fig,fig2

        
    def snx():
        token_ticker = "SNX"
        coingecko_id = "havven"
        entry_price = 3.1
        vesting_schedule = {pd.Timestamp('2021-12-02'):100}
        tge_date = "2018-03-21"
        total_tokens_number = 241936

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)


        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_snx = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_snx.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_snx.loc[date, 'current_roi'] = round(current_roi, 2)
            df_snx.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_snx.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_snx.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_snx.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_snx.index = df_snx.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_snx['next_vesting_date'] = df_snx['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_snx = df_snx.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_snx.rename(columns={'price': 'token_price'}, inplace=True)
        df_snx['ROI'] = (df_snx['token_price'] - entry_price) / entry_price * 100

        fig, ax = plt.subplots()
        ax.plot(df_snx.index, df_snx['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_snx.index, df_snx['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_snx,fig,fig2

    
    def ata1():
        token_ticker1 = "ATA"
        coingecko_id1 = "automata"
        entry_price = 0.02
        vesting_schedule = {pd.Timestamp('2021-06-07'):12.5,pd.Timestamp('2021-12-07'):12.5,pd.Timestamp('2022-03-07'):12.5,pd.Timestamp('2022-06-07'):12.5,
                            pd.Timestamp('2022-09-07'):12.5,pd.Timestamp('2022-12-07'):12.5,pd.Timestamp('2023-03-07'):12.5,pd.Timestamp('2023-06-07'):12.5}
        tge_date = "2021-06-07"
        total_tokens_number = 4800000

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id1}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id1}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id1]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)

        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_ata1 = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_ata1.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_ata1.loc[date, 'current_roi'] = round(current_roi, 2)
            df_ata1.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_ata1.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_ata1.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_ata1.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_ata1.index = df_ata1.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_ata1['next_vesting_date'] = df_ata1['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_ata1 = df_ata1.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_ata1.rename(columns={'price': 'token_price'}, inplace=True)
        df_ata1['ROI'] = (df_ata1['token_price'] - entry_price) / entry_price * 100

        
        fig, ax = plt.subplots()
        ax.plot(df_ata1.index, df_ata1['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_ata1.index, df_ata1['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_ata1,fig,fig2

    def ata2():
        token_ticker2 = "ATA"
        coingecko_id2 = "automata"
        entry_price = 0.04
        vesting_schedule = {pd.Timestamp('2021-06-07'):12.5,pd.Timestamp('2021-12-07'):12.5,pd.Timestamp('2022-03-07'):12.5,pd.Timestamp('2022-06-07'):12.5,pd.Timestamp('2022-09-07'):12.5,
                            pd.Timestamp('2022-12-07'):12.5,pd.Timestamp('2023-03-07'):12.5,pd.Timestamp('2023-06-07'):12.5}
        tge_date = "2021-06-07"
        total_tokens_number = 3750000

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id2}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id2}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id2]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)


        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_ata2 = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_ata2.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_ata2.loc[date, 'current_roi'] = round(current_roi, 2)
            df_ata2.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_ata2.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_ata2.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_ata2.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_ata2.index = df_ata2.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_ata2['next_vesting_date'] = df_ata2['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_ata2 = df_ata2.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_ata2.rename(columns={'price': 'token_price'}, inplace=True)
        df_ata2['ROI'] = (df_ata2['token_price'] - entry_price) / entry_price * 100

        
        fig, ax = plt.subplots()
        ax.plot(df_ata2.index, df_ata2['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_ata2.index, df_ata2['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_ata2,fig,fig2

    def lqty():
        token_ticker = "LQTY"
        coingecko_id = "liquity"
        entry_price = 0.699
        vesting_schedule = {pd.Timestamp('2022-04-05'):25,pd.Timestamp('2022-05-05'):2.77,pd.Timestamp('2022-06-05'):2.77,pd.Timestamp('2022-07-05'):2.77,pd.Timestamp('2022-08-05'):2.77,
                            pd.Timestamp('2022-09-05'):2.77,pd.Timestamp('2022-10-05'):2.77,pd.Timestamp('2022-11-05'):2.78,pd.Timestamp('2022-12-05'):2.78,pd.Timestamp('2023-01-05'):2.78,
                            pd.Timestamp('2023-02-05'):2.78,pd.Timestamp('2023-03-05'):2.78,pd.Timestamp('2023-04-05'):2.78,pd.Timestamp('2023-05-05'):2.78,pd.Timestamp('2023-06-05'):2.78,
                            pd.Timestamp('2023-07-05'):2.78,pd.Timestamp('2023-08-05'):2.78,pd.Timestamp('2023-09-05'):2.78,pd.Timestamp('2023-10-05'):2.78,pd.Timestamp('2023-11-05'):2.78,
                            pd.Timestamp('2023-12-05'):2.78,pd.Timestamp('2024-01-05'):2.78,pd.Timestamp('2024-02-05'):2.78,pd.Timestamp('2024-03-05'):2.78,pd.Timestamp('2024-04-05'):2.78,
                            pd.Timestamp('2024-05-05'):2.78,pd.Timestamp('2024-06-05'):2.78,pd.Timestamp('2024-07-05'):2.78
                            }
        tge_date = "2021-04-05"
        total_tokens_number = 357143

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)


        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_lqty = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_lqty.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_lqty.loc[date, 'current_roi'] = round(current_roi, 2)
            df_lqty.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_lqty.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_lqty.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_lqty.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_lqty.index = df_lqty.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_lqty['next_vesting_date'] = df_lqty['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_lqty = df_lqty.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_lqty.rename(columns={'price': 'token_price'}, inplace=True)
        df_lqty['ROI'] = (df_lqty['token_price'] - entry_price) / entry_price * 100

        
        fig, ax = plt.subplots()
        ax.plot(df_lqty.index, df_lqty['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_lqty.index, df_lqty['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_lqty,fig,fig2

    def c98():
        token_ticker = "C98"
        coingecko_id = "coin98"
        entry_price = 0.075
        vesting_schedule = {pd.Timestamp('2022-07-23'):1.92,pd.Timestamp('2022-05-05'):2.77,pd.Timestamp('2022-06-05'):2.77,pd.Timestamp('2022-07-05'):2.77,pd.Timestamp('2022-08-05'):2.77,
                            pd.Timestamp('2022-09-05'):2.77,pd.Timestamp('2022-10-05'):2.77,pd.Timestamp('2022-11-05'):2.77,pd.Timestamp('2022-12-05'):2.77,pd.Timestamp('2023-01-05'):2.77,
                            pd.Timestamp('2023-02-05'):2.77,pd.Timestamp('2023-03-05'):2.77,pd.Timestamp('2023-04-05'):2.77,pd.Timestamp('2023-05-05'):2.77,pd.Timestamp('2023-06-05'):2.77,
                            pd.Timestamp('2023-07-05'):2.77,pd.Timestamp('2023-08-05'):2.77,pd.Timestamp('2023-09-05'):2.77,pd.Timestamp('2023-10-05'):2.77,pd.Timestamp('2023-11-05'):2.77,
                            pd.Timestamp('2023-12-05'):2.77,pd.Timestamp('2024-01-05'):2.77,pd.Timestamp('2024-02-05'):2.77,pd.Timestamp('2024-03-05'):2.77,pd.Timestamp('2024-04-05'):2.77,
                            pd.Timestamp('2024-05-05'):2.77,pd.Timestamp('2024-06-05'):2.77,pd.Timestamp('2024-07-05'):2.77,pd.Timestamp('2024-08-05'):2.77,pd.Timestamp('2024-09-05'):2.77,
                            pd.Timestamp('2024-10-05'):2.77,pd.Timestamp('2024-11-05'):2.77,pd.Timestamp('2024-12-05'):2.77,pd.Timestamp('2025-01-05'):2.77,pd.Timestamp('2025-02-05'):2.77,
                            pd.Timestamp('2025-03-05'):2.77,pd.Timestamp('2023-07-23'):2.77}
        tge_date = "2021-07-23"
        total_tokens_number = 2666667

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)

        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_c98 = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_c98.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_c98.loc[date, 'current_roi'] = round(current_roi, 2)
            df_c98.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_c98.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_c98.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_c98.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_c98.index = df_c98.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_c98['next_vesting_date'] = df_c98['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_c98 = df_c98.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_c98.rename(columns={'price': 'token_price'}, inplace=True)
        df_c98['ROI'] = (df_c98['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_c98.index, df_c98['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_c98.index, df_c98['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROi in %')
        ax.set_title('ROi in %')
        
        return df_c98,fig,fig2

    def uma():
        token_ticker = "UMA"
        coingecko_id = "uma"
        entry_price = 0.963
        vesting_schedule = {pd.Timestamp('2021-08-31'):100}
        tge_date = "2020-04-30"
        total_tokens_number = 6893

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)

        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_uma = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_uma.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_uma.loc[date, 'current_roi'] = round(current_roi, 2)
            df_uma.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_uma.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_uma.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_uma.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_uma.index = df_uma.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_uma['next_vesting_date'] = df_uma['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_uma = df_uma.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_uma.rename(columns={'price': 'token_price'}, inplace=True)
        df_uma['ROI'] = (df_uma['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_uma.index, df_uma['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_uma.index, df_uma['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_uma,fig,fig2

    def mux():
        token_ticker = "MUX"
        coingecko_id = "mcdex"
        entry_price = 10
        vesting_schedule = {pd.Timestamp('2021-08-31'):100}
        tge_date = "2020-07-13"
        total_tokens_number = 20000

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)

        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_mcdex = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_mcdex.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_mcdex.loc[date, 'current_roi'] = round(current_roi, 2)
            df_mcdex.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_mcdex.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_mcdex.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_mcdex.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_mcdex.index = df_mcdex.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_mcdex['next_vesting_date'] = df_mcdex['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_mcdex = df_mcdex.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_mcdex.rename(columns={'price': 'token_price'}, inplace=True)
        df_mcdex['ROI'] = (df_mcdex['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_mcdex.index, df_mcdex['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_mcdex.index, df_mcdex['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_mcdex, fig,fig2

    def izi():
        token_ticker = "IZI"
        coingecko_id = "izumi-finance"
        entry_price = 0.02
        vesting_schedule = {pd.Timestamp('2022-12-21'):100}
        tge_date = "2021-12-21"
        total_tokens_number = 16150000

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)


        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_izumi = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_izumi.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_izumi.loc[date, 'current_roi'] = round(current_roi, 2)
            df_izumi.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_izumi.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_izumi.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_izumi.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_izumi.index = df_izumi.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_izumi['next_vesting_date'] = df_izumi['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_izumi = df_izumi.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_izumi.rename(columns={'price': 'token_price'}, inplace=True)
        df_izumi['ROI'] = (df_izumi['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_izumi.index, df_izumi['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_izumi.index, df_izumi['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_izumi, fig,fig2

    def insur():
        token_ticker = "INSUR"
        coingecko_id = "insurace"
        entry_price = 0.35
        vesting_schedule = {pd.Timestamp('2023-05-15'):100}
        tge_date = "2021-03-15"
        total_tokens_number = 228571

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)


        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_insur = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_insur.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_insur.loc[date, 'current_roi'] = round(current_roi, 2)
            df_insur.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_insur.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_insur.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_insur.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_insur.index = df_insur.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_insur['next_vesting_date'] = df_insur['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_insur = df_insur.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_insur.rename(columns={'price': 'token_price'}, inplace=True)
        df_insur['ROI'] = (df_insur['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_insur.index, df_insur['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_insur.index, df_insur['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_insur, fig,fig2

    def thales():
        token_ticker = "THALES"
        coingecko_id = "thales"
        entry_price = 0.33
        vesting_schedule = {pd.Timestamp('2022-09-16'):50,pd.Timestamp('2022-10-16'):4.17,pd.Timestamp('2022-11-16'):4.17,pd.Timestamp('2022-12-16'):4.17,pd.Timestamp('2023-01-16'):4.17,
                            pd.Timestamp('2023-02-16'):4.17,pd.Timestamp('2023-03-16'):4.17,pd.Timestamp('2023-04-16'):4.17,pd.Timestamp('2023-05-16'):4.17,pd.Timestamp('2023-06-16'):4.16,
                            pd.Timestamp('2023-07-16'):4.16,pd.Timestamp('2023-08-16'):4.16,pd.Timestamp('2023-09-16'):4.16}
        tge_date = "2021-09-16"
        total_tokens_number = 303030

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)


        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_thales = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_thales.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_thales.loc[date, 'current_roi'] = round(current_roi, 2)
            df_thales.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_thales.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_thales.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_thales.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_thales.index = df_thales.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_thales['next_vesting_date'] = df_thales['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_thales = df_thales.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_thales.rename(columns={'price': 'token_price'}, inplace=True)
        df_thales['ROI'] = (df_thales['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_thales.index, df_thales['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_thales.index, df_thales['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_thales, fig,fig2

    def imf():
        token_ticker = "IF"
        coingecko_id = "impossible-finance"
        entry_price = 0.06
        vesting_schedule = {pd.Timestamp('2021-06-18'):25,pd.Timestamp('2022-07-18'):6.25,pd.Timestamp('2022-08-18'):6.25,pd.Timestamp('2022-09-18'):6.25,pd.Timestamp('2022-10-18'):6.25,
                            pd.Timestamp('2022-11-18'):6.25,pd.Timestamp('2022-12-18'):6.25,pd.Timestamp('2023-01-18'):6.25,pd.Timestamp('2023-02-18'):6.25,pd.Timestamp('2023-03-18'):6.25,
                            pd.Timestamp('2023-04-18'):6.25,pd.Timestamp('2023-05-18'):6.25,pd.Timestamp('2023-06-18'):6.25}
        tge_date = "2021-06-18"
        total_tokens_number =   1666666.67 

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)

        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_if = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_if.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_if.loc[date, 'current_roi'] = round(current_roi, 2)
            df_if.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_if.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_if.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_if.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_if.index = df_if.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_if['next_vesting_date'] = df_if['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_if = df_if.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_if.rename(columns={'price': 'token_price'}, inplace=True)
        df_if['ROI'] = (df_if['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_if.index, df_if['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_if.index, df_if['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_if, fig,fig2

    def glmr():
        token_ticker = "GLMR"
        coingecko_id = "moonbeam"
        entry_price = 0.05
        vesting_schedule = {pd.Timestamp('2023-01-11'):100}
        tge_date = "2022-02-11"
        total_tokens_number = 5000000

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)


        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_glmr = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_glmr.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_glmr.loc[date, 'current_roi'] = round(current_roi, 2)
            df_glmr.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_glmr.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_glmr.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_glmr.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_glmr.index = df_glmr.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_glmr['next_vesting_date'] = df_glmr['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_glmr = df_glmr.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_glmr.rename(columns={'price': 'token_price'}, inplace=True)
        df_glmr['ROI'] = (df_glmr['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_glmr.index, df_glmr['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_glmr.index, df_glmr['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_glmr, fig,fig2

    def astr():
        token_ticker = "ASTR"
        coingecko_id = "astar"
        entry_price =   19366666/83000
        vesting_schedule = {pd.Timestamp('2022-07-17'):100}
        tge_date = "2022-01-17"
        total_tokens_number = 19366666

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)


        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_astr = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_astr.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_astr.loc[date, 'current_roi'] = round(current_roi, 2)
            df_astr.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_astr.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_astr.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_astr.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_astr.index = df_astr.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_astr['next_vesting_date'] = df_astr['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_astr = df_astr.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_astr.rename(columns={'price': 'token_price'}, inplace=True)
        df_astr['ROI'] = (df_astr['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_astr.index, df_astr['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_astr.index, df_astr['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_astr, fig,fig2

    def ujenny():
        token_ticker = "UJENNY"
        coingecko_id = "jenny-metaverse-dao-token"
        entry_price = 1.345 
        vesting_schedule = {pd.Timestamp('2021-05-16'):100}
        tge_date = "2021-05-13"
        total_tokens_number = 148699 

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)

        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_ujenny = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_ujenny.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_ujenny.loc[date, 'current_roi'] = round(current_roi, 2)
            df_ujenny.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_ujenny.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_ujenny.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_ujenny.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_ujenny.index = df_ujenny.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_ujenny['next_vesting_date'] = df_ujenny['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_ujenny = df_ujenny.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_ujenny.rename(columns={'price': 'token_price'}, inplace=True)
        df_ujenny['ROI'] = (df_ujenny['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_ujenny.index, df_ujenny['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_ujenny.index, df_ujenny['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_ujenny, fig,fig2

    def fnx():
        token_ticker = "FNX"
        coingecko_id = "FinNexus"
        entry_price = 0.12
        vesting_schedule = {pd.Timestamp('2022-07-03'):100}
        tge_date = "2021-08-13"
        total_tokens_number = 1250000

        # call coingecko api to get real-time price
        #url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        #response = requests.get(url)
        #price = response.json()[coingecko_id]["usd"]

        # calculate current ROI
        #current_price = price
        #current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_fnx = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_fnx.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_fnx.loc[date, 'current_roi'] = 'N/A'
            df_fnx.loc[date, 'current_usd_amount'] = 'N/A'
            df_fnx.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_fnx.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_fnx.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_fnx.index = df_fnx.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_fnx['next_vesting_date'] = df_fnx['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        fig, ax = plt.subplots()
        ax.plot(df_fnx.index, df_fnx['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        return df_fnx, fig

    def swise():
        token_ticker = "SWISE"
        coingecko_id = "stakewise"
        entry_price = 0.12
        vesting_schedule = {pd.Timestamp('2022-06-20'):5.65,pd.Timestamp('2022-07-20'):5.55,pd.Timestamp('2022-08-20'):5.55,pd.Timestamp('2022-09-20'):5.55,
                            pd.Timestamp('2022-10-20'):5.55,pd.Timestamp('2022-11-20'):5.55,pd.Timestamp('2022-12-20'):5.55,pd.Timestamp('2023-01-20'):5.55,
                            pd.Timestamp('2023-02-20'):5.55,pd.Timestamp('2023-03-20'):5.55,pd.Timestamp('2023-04-20'):5.55,pd.Timestamp('2023-05-20'):5.55,
                            pd.Timestamp('2023-06-20'):5.55,pd.Timestamp('2023-07-20'):5.55,pd.Timestamp('2023-08-20'):5.55,pd.Timestamp('2023-09-20'):5.55,
                            pd.Timestamp('2023-10-20'):5.55,pd.Timestamp('2023-11-20'):5.55}
        tge_date = "2021-04-27"
        total_tokens_number = 3333333.33 

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)


        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_swise = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_swise.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_swise.loc[date, 'current_roi'] = round(current_roi, 2)
            df_swise.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_swise.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_swise.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_swise.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_swise.index = df_swise.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_swise['next_vesting_date'] = df_swise['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_swise = df_swise.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_swise.rename(columns={'price': 'token_price'}, inplace=True)
        df_swise['ROI'] = (df_swise['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_swise.index, df_swise['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_swise.index, df_swise['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_swise, fig,fig2

    def cfg():
        token_ticker = "CFG"
        coingecko_id = "centrifuge"
        entry_price = 0.12
        vesting_schedule = {pd.Timestamp('2021-12-16'):50,pd.Timestamp('2022-01-16'):2.9,pd.Timestamp('2022-01-16'):2.083,pd.Timestamp('2022-02-16'):2.083,
                            pd.Timestamp('2022-03-16'):2.083,pd.Timestamp('2022-04-16'):2.083,pd.Timestamp('2022-05-16'):2.083,pd.Timestamp('2022-06-16'):2.083,
                            pd.Timestamp('2022-07-16'):2.083,pd.Timestamp('2022-08-16'):2.083,pd.Timestamp('2022-09-16'):2.083,pd.Timestamp('2022-10-16'):2.083,
                            pd.Timestamp('2022-11-16'):2.083,pd.Timestamp('2022-12-16'):2.083,pd.Timestamp('2023-01-16'):2.083,pd.Timestamp('2023-02-16'):2.083,
                            pd.Timestamp('2023-03-16'):2.083,pd.Timestamp('2023-04-16'):2.083,pd.Timestamp('2023-05-16'):2.083,pd.Timestamp('2023-06-16'):2.083,
                            pd.Timestamp('2023-07-16'):2.083,pd.Timestamp('2023-08-16'):2.083,pd.Timestamp('2023-09-16'):2.083,pd.Timestamp('2023-10-16'):2.083,
                            pd.Timestamp('2023-11-16'):2.083,pd.Timestamp('2023-12-16'):2.083}
        tge_date = "2021-05-28"
        total_tokens_number = 1666666.67 

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)


        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_cfg = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_cfg.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_cfg.loc[date, 'current_roi'] = round(current_roi, 2)
            df_cfg.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_cfg.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_cfg.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_cfg.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_cfg.index = df_cfg.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_cfg['next_vesting_date'] = df_cfg['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_cfg = df_cfg.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_cfg.rename(columns={'price': 'token_price'}, inplace=True)
        df_cfg['ROI'] = (df_cfg['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_cfg.index, df_cfg['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_cfg.index, df_cfg['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_cfg, fig,fig2

    def gxy():
        token_ticker = "GXY"
        coingecko_id = "galxe"
        entry_price = 0.075
        vesting_schedule = {pd.Timestamp('2022-02-17'):12,pd.Timestamp('2022-05-17'):11,pd.Timestamp('2022-08-17'):11,pd.Timestamp('2022-11-17'):11,
                            pd.Timestamp('2023-02-17'):11,pd.Timestamp('2023-05-17'):11,pd.Timestamp('2023-08-17'):11,pd.Timestamp('2023-11-17'):11,
                            pd.Timestamp('2024-02-17'):11}
        tge_date = "2022-02-17"
        total_tokens_number = 1333333.33 

        # call coingecko api to get real-time price
        #url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        #response = requests.get(url)
        #price = response.json()[coingecko_id]["usd"]

        # calculate current ROI
        #current_price = price
        #current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_gxy = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_gxy.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_gxy.loc[date, 'current_roi'] = 'N/A'
            df_gxy.loc[date, 'current_usd_amount'] = 'N/A'
            df_gxy.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_gxy.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_gxy.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_gxy.index = df_gxy.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_gxy['next_vesting_date'] = df_gxy['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        fig, ax = plt.subplots()
        ax.plot(df_gxy.index, df_gxy['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        return df_gxy, fig

    def kyve():
        token_ticker = "KYVE"
        coingecko_id = "Kyve network"
        entry_price = 0.1
        vesting_schedule = {pd.Timestamp('2022-12-31'):10,pd.Timestamp('2023-01-31'):5,pd.Timestamp('2023-02-28'):5,pd.Timestamp('2023-03-31'):5,pd.Timestamp('2023-04-30'):5
                            ,pd.Timestamp('2023-05-31'):5,pd.Timestamp('2023-06-30'):5,pd.Timestamp('2023-07-31'):5,pd.Timestamp('2023-08-31'):5,pd.Timestamp('2023-09-30'):5
                            ,pd.Timestamp('2023-10-31'):5,pd.Timestamp('2023-11-30'):5,pd.Timestamp('2023-12-31'):5,pd.Timestamp('2024-01-31'):5,pd.Timestamp('2024-02-28'):5
                            ,pd.Timestamp('2024-03-31'):5,pd.Timestamp('2024-04-30'):5,pd.Timestamp('2024-05-31'):5,pd.Timestamp('2024-06-30'):5}
        tge_date = "2022-12-31"
        total_tokens_number = 1333333.33 

        # call coingecko api to get real-time price
        #url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        #response = requests.get(url)
        #price = response.json()[coingecko_id]["usd"]

        # calculate current ROI
        #current_price = price
        #current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_kyve = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_kyve.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_kyve.loc[date, 'current_roi'] = 'N/A'
            df_kyve.loc[date, 'current_usd_amount'] = 'N/A'
            df_kyve.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_kyve.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_kyve.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_kyve.index = df_kyve.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_kyve['next_vesting_date'] = df_kyve['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        fig, ax = plt.subplots()
        ax.plot(df_kyve.index, df_kyve['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        return df_kyve, fig

    def mina():
        token_ticker = "MINA"
        coingecko_id = "mina-protocol"
        entry_price = 1.86
        vesting_schedule = {pd.Timestamp('2023-02-27'):50,pd.Timestamp('2024-02-27'):2.9}
        tge_date = "2021-06-01"
        total_tokens_number = 537634

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)


        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_mina = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_mina.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_mina.loc[date, 'current_roi'] = round(current_roi, 2)
            df_mina.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_mina.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_mina.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_mina.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_mina.index = df_mina.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_mina['next_vesting_date'] = df_mina['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_mina = df_mina.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_mina.rename(columns={'price': 'token_price'}, inplace=True)
        df_mina['ROI'] = (df_mina['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_mina.index, df_mina['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_mina.index, df_mina['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_mina, fig,fig2

    def meta():
        token_ticker = "META"
        coingecko_id = "meta-pool"
        entry_price = 0.0006
        vesting_schedule = {}
        start_date = pd.Timestamp('2023-04-26')
        end_date = start_date + pd.DateOffset(days=364)

        for single_date in pd.date_range(start=start_date, end=end_date):
            vesting_schedule[single_date] = 100/365

        tge_date = "2022-03-12"
        total_tokens_number = 1000000000
        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)

        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_meta = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_meta.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_meta.loc[date, 'current_roi'] = round(current_roi, 2)
            df_meta.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_meta.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_meta.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_meta.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_meta.index = df_meta.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_meta['next_vesting_date'] = df_meta['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_meta = df_meta.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_meta.rename(columns={'price': 'token_price'}, inplace=True)
        df_meta['ROI'] = (df_meta['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_meta.index, df_meta['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_meta.index, df_meta['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_meta, fig,fig2

    def cpr():
        token_ticker = "CPR"
        coingecko_id = "cipher-2"
        entry_price = 0.000926
        vesting_schedule = {pd.Timestamp('2022-09-01'):20,pd.Timestamp('2022-12-01'):10,pd.Timestamp('2023-03-01'):10,
                            pd.Timestamp('2023-06-01'):10,pd.Timestamp('2023-09-01'):10,pd.Timestamp('2023-12-01'):10,
                            pd.Timestamp('2024-03-01'):10,pd.Timestamp('2024-06-01'):10,pd.Timestamp('2024-09-01'):10}
        tge_date = "2022-09-01"
        total_tokens_number = 54000000

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)

        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_cpr = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_cpr.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_cpr.loc[date, 'current_roi'] = round(current_roi, 2)
            df_cpr.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_cpr.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_cpr.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_cpr.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_cpr.index = df_cpr.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_cpr['next_vesting_date'] = df_cpr['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_cpr = df_cpr.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_cpr.rename(columns={'price': 'token_price'}, inplace=True)
        df_cpr['ROI'] = (df_cpr['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_cpr.index, df_cpr['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_cpr.index, df_cpr['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_cpr, fig,fig2

    def stark():
        #vtoken_ticker = "CPR"
        coingecko_id = "starkware"
        entry_price = 1.93
        vesting_schedule = {pd.Timestamp('2022-11-01'):25,pd.Timestamp('2022-12-01'):2.083,pd.Timestamp('2023-01-01'):2.083,
                            pd.Timestamp('2023-02-01'):2.083,pd.Timestamp('2023-03-01'):2.083,pd.Timestamp('2023-04-01'):2.083,
                            pd.Timestamp('2023-05-01'):2.083,pd.Timestamp('2023-06-01'):2.083,pd.Timestamp('2023-07-01'):2.083,
                            pd.Timestamp('2023-08-01'):2.083,pd.Timestamp('2023-09-01'):2.083,pd.Timestamp('2023-10-01'):2.083,
                            pd.Timestamp('2023-11-01'):2.083,pd.Timestamp('2023-12-01'):2.083,pd.Timestamp('2024-01-01'):2.083,
                            pd.Timestamp('2024-02-01'):2.083,pd.Timestamp('2024-03-01'):2.083,pd.Timestamp('2024-04-01'):2.083,
                            pd.Timestamp('2024-05-01'):2.083,pd.Timestamp('2024-06-01'):2.083,pd.Timestamp('2024-07-01'):2.083,
                            pd.Timestamp('2024-08-01'):2.083,pd.Timestamp('2024-09-01'):2.083,pd.Timestamp('2024-10-01'):2.083,
                            pd.Timestamp('2024-11-01'):2.083,pd.Timestamp('2024-12-01'):2.083,pd.Timestamp('2025-01-01'):2.083,
                            pd.Timestamp('2025-02-01'):2.084,pd.Timestamp('2025-03-01'):2.084,pd.Timestamp('2025-04-01'):2.084,
                            pd.Timestamp('2025-05-01'):2.084,pd.Timestamp('2025-06-01'):2.084,pd.Timestamp('2025-07-01'):2.084,
                            pd.Timestamp('2025-08-01'):2.084,pd.Timestamp('2025-09-01'):2.084,pd.Timestamp('2025-10-01'):2.084,
                            pd.Timestamp('2025-11-01'):2.084}
        tge_date = "2022-01-31"
        total_tokens_number = 96318

        # call coingecko api to get real-time price
        #url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        #response = requests.get(url)
        #price = response.json()[coingecko_id]["usd"]

        # calculate current ROI
        current_price = 0.036
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_stark = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_stark.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_stark.loc[date, 'current_roi'] = round(current_roi, 2)
            df_stark.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_stark.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_stark.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_stark.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_stark.index = df_stark.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_stark['next_vesting_date'] = df_stark['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        fig, ax = plt.subplots()
        ax.plot(df_stark.index, df_stark['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        return df_stark, fig

    def aurora():
        token_ticker = "AURORA"
        coingecko_id = "aurora-near"
        entry_price = 0.15
        vesting_schedule = {pd.Timestamp('2022-05-18'):3.25,pd.Timestamp('2022-08-18'):3.25,pd.Timestamp('2022-11-18'):3.5,
                            pd.Timestamp('2023-02-18'):10,pd.Timestamp('2023-05-18'):10,pd.Timestamp('2023-08-18'):10,
                            pd.Timestamp('2023-11-18'):10,pd.Timestamp('2024-02-18'):10,pd.Timestamp('2024-05-18'):10,
                            pd.Timestamp('2024-08-18'):10,pd.Timestamp('2024-11-18'):10,pd.Timestamp('2025-02-18'):10}
        tge_date = "2021-11-18"
        total_tokens_number = 1000000

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)


        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_aurora = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_aurora.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_aurora.loc[date, 'current_roi'] = round(current_roi, 2)
            df_aurora.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_aurora.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_aurora.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_aurora.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_aurora.index = df_aurora.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_aurora['next_vesting_date'] = df_aurora['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_aurora = df_aurora.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_aurora.rename(columns={'price': 'token_price'}, inplace=True)
        df_aurora['ROI'] = (df_aurora['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_aurora.index, df_aurora['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_aurora.index, df_aurora['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_aurora, fig,fig2

    def rice():
        token_ticker = "RICE"
        coingecko_id = "daosquare"
        entry_price = 0.135
        vesting_schedule = {pd.Timestamp('2022-07-16'):10,pd.Timestamp('2022-10-16'):10,
                            pd.Timestamp('2023-01-16'):10,pd.Timestamp('2023-04-16'):10,pd.Timestamp('2023-07-16'):10,
                            pd.Timestamp('2023-10-16'):10,pd.Timestamp('2024-01-16'):10,pd.Timestamp('2024-04-16'):10,
                            pd.Timestamp('2024-07-16'):10,pd.Timestamp('2024-10-16'):10}
        tge_date = "2021-10-16"
        total_tokens_number = 370370

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)

        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_rice = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_rice.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_rice.loc[date, 'current_roi'] = round(current_roi, 2)
            df_rice.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_rice.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_rice.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_rice.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_rice.index = df_rice.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_rice['next_vesting_date'] = df_rice['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_rice = df_rice.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_rice.rename(columns={'price': 'token_price'}, inplace=True)
        df_rice['ROI'] = (df_rice['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_rice.index, df_rice['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_rice.index, df_rice['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_rice, fig,fig2

    def brrr():
        token_ticker = "BRRR"
        coingecko_id = "burrow"
        entry_price = 0.05
        vesting_schedule = {pd.Timestamp('2022-12-15'):50,pd.Timestamp('2023-01-15'):50/12,
                            pd.Timestamp('2023-02-15'):50/12,pd.Timestamp('2023-03-15'):50/12,pd.Timestamp('2023-04-15'):50/12,
                            pd.Timestamp('2023-05-15'):50/12,pd.Timestamp('2023-06-15'):50/12,pd.Timestamp('2023-07-15'):50/12,
                            pd.Timestamp('2023-08-15'):50/12,pd.Timestamp('2023-09-15'):50/12,pd.Timestamp('2023-10-15'):50/12,
                            pd.Timestamp('2023-11-15'):50/12,pd.Timestamp('2023-12-15'):50/12}
        tge_date = "2022-06-09"
        total_tokens_number = 2000000

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)

        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_brrr = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_brrr.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_brrr.loc[date, 'current_roi'] = round(current_roi, 2)
            df_brrr.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_brrr.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_brrr.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_brrr.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_brrr.index = df_brrr.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_brrr['next_vesting_date'] = df_brrr['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_brrr = df_brrr.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_brrr.rename(columns={'price': 'token_price'}, inplace=True)
        df_brrr['ROI'] = (df_brrr['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_brrr.index, df_brrr['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_brrr.index, df_brrr['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_brrr, fig,fig2

    def gtc():
        token_ticker = "GTC"
        coingecko_id = "gitcoin"
        entry_price = 1.6
        vesting_schedule = {pd.Timestamp('2023-11-01'):100/12,pd.Timestamp('2023-12-01'):100/12,pd.Timestamp('2024-01-01'):100/12,
                            pd.Timestamp('2024-02-01'):100/12,pd.Timestamp('2024-03-01'):100/12,pd.Timestamp('2024-04-01'):100/12,
                            pd.Timestamp('2024-05-01'):100/12,pd.Timestamp('2024-06-01'):100/12,pd.Timestamp('2024-07-01'):100/12,
                            pd.Timestamp('2024-08-01'):100/12,pd.Timestamp('2024-09-01'):100/12,pd.Timestamp('2024-10-01'):100/12}
        tge_date = "2021-05-25"
        total_tokens_number = 468750

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)


        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=pd.Timestamp('2023-01-01'), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_gtc = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_gtc.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_gtc.loc[date, 'current_roi'] = round(current_roi, 2)
            df_gtc.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_gtc.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_gtc.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_gtc.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_gtc.index = df_gtc.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_gtc['next_vesting_date'] = df_gtc['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_gtc = df_gtc.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_gtc.rename(columns={'price': 'token_price'}, inplace=True)
        df_gtc['ROI'] = (df_gtc['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_gtc.index, df_gtc['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_gtc.index, df_gtc['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_gtc, fig,fig2

    def magic():
        token_ticker = "MAGIC"
        coingecko_id = "magic"
        entry_price = 0.230072024
        vesting_schedule = {pd.Timestamp('2023-11-18'):100/24,pd.Timestamp('2023-12-18'):100/24,pd.Timestamp('2024-01-18'):100/24,
                            pd.Timestamp('2024-02-18'):100/24,pd.Timestamp('2024-03-18'):100/24,pd.Timestamp('2024-04-18'):100/24,
                            pd.Timestamp('2024-05-18'):100/24,pd.Timestamp('2024-06-18'):100/24,pd.Timestamp('2024-07-18'):100/24,
                            pd.Timestamp('2024-08-18'):100/24,pd.Timestamp('2024-09-18'):100/24,pd.Timestamp('2024-10-18'):100/24,
                            pd.Timestamp('2024-11-18'):100/24,pd.Timestamp('2024-12-18'):100/24,pd.Timestamp('2025-01-18'):100/24,
                            pd.Timestamp('2025-02-18'):100/24,pd.Timestamp('2025-03-18'):100/24,pd.Timestamp('2025-04-18'):100/24,
                            pd.Timestamp('2025-05-18'):100/24,pd.Timestamp('2025-06-18'):100/24,pd.Timestamp('2025-07-18'):100/24,
                            pd.Timestamp('2025-08-18'):100/24,pd.Timestamp('2025-09-18'):100/24,pd.Timestamp('2025-10-18'):100/24,
                            }
        tge_date = "2021-09-27"
        total_tokens_number = 869293

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)


        # calculate current ROI
        current_price = price
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=pd.Timestamp('2023-01-01'), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_magic = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_magic.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_magic.loc[date, 'current_roi'] = round(current_roi, 2)
            df_magic.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_magic.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_magic.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_magic.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_magic.index = df_magic.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_magic['next_vesting_date'] = df_magic['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_magic = df_magic.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_magic.rename(columns={'price': 'token_price'}, inplace=True)
        df_magic['ROI'] = (df_magic['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_magic.index, df_magic['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_magic.index, df_magic['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        
        return df_magic, fig,fig2

    def ali():
        token_ticker = "ALI"
        coingecko_id = "alethea-artificial-liquid-intelligence-token"
        entry_price = 0.01
        vesting_schedule = {pd.Timestamp('2023-11-18'):100/24,pd.Timestamp('2023-12-18'):100/24,pd.Timestamp('2024-01-18'):100/24,
                            pd.Timestamp('2024-02-18'):100/24,pd.Timestamp('2024-03-18'):100/24,pd.Timestamp('2024-04-18'):100/24,
                            pd.Timestamp('2024-05-18'):100/24,pd.Timestamp('2024-06-18'):100/24,pd.Timestamp('2024-07-18'):100/24,
                            pd.Timestamp('2024-08-18'):100/24,pd.Timestamp('2024-09-18'):100/24,pd.Timestamp('2024-10-18'):100/24,
                            pd.Timestamp('2024-11-18'):100/24,pd.Timestamp('2024-12-18'):100/24,pd.Timestamp('2025-01-18'):100/24,
                            pd.Timestamp('2025-02-18'):100/24,pd.Timestamp('2025-03-18'):100/24,pd.Timestamp('2025-04-18'):100/24,
                            pd.Timestamp('2025-05-18'):100/24,pd.Timestamp('2025-06-18'):100/24,pd.Timestamp('2025-07-18'):100/24,
                            pd.Timestamp('2025-08-18'):100/24,pd.Timestamp('2025-09-18'):100/24,pd.Timestamp('2025-10-18'):100/24,
                            }
        tge_date = "2022-02-14"
        total_tokens_number = 25000000

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)


        # calculate current ROI
        current_price = 1.05
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=pd.Timestamp('2023-01-01'), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_ali = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_ali.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_ali.loc[date, 'current_roi'] = round(current_roi, 2)
            df_ali.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_ali.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_ali.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_ali.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_ali.index = df_ali.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_ali['next_vesting_date'] = df_ali['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_ali = df_ali.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_ali.rename(columns={'price': 'token_price'}, inplace=True)
        df_ali['ROI'] = (df_ali['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_ali.index, df_ali['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_ali.index, df_ali['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_ali, fig,fig2

    def perc():
        token_ticker = "PERC"
        coingecko_id = "perion"
        entry_price = 0.6
        vesting_schedule = {pd.Timestamp('2022-02-06'):10,pd.Timestamp('2023-02-03'):90/12,pd.Timestamp('2023-03-03'):90/12,
                            pd.Timestamp('2023-04-03'):90/12,pd.Timestamp('2023-05-03'):90/12,pd.Timestamp('2023-06-03'):90/12,
                            pd.Timestamp('2023-07-03'):90/12,pd.Timestamp('2023-08-03'):90/12,pd.Timestamp('2023-09-03'):90/12,
                            pd.Timestamp('2023-10-03'):90/12,pd.Timestamp('2023-11-03'):90/12,pd.Timestamp('2023-12-03'):90/12,
                            pd.Timestamp('2024-01-03'):90/12,pd.Timestamp('2024-02-03'):100/12,
                            }
        tge_date = "2022-02-03"
        total_tokens_number = 1000000

        # call coingecko api to get real-time price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
        url1 = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=max"
        response = requests.get(url)
        response1 = requests.get(url1)
        price = response.json()[coingecko_id]["usd"]
        price1 = response1.json()
        # Convert the timestamp to datetime format and extract the date
        dfdf = pd.DataFrame(price1['prices'], columns=['timestamp', 'price'])
        dfdf['timestamp'] = pd.to_datetime(dfdf['timestamp'], unit='ms').dt.date

        # Set the date as the index
        dfdf.set_index('timestamp', inplace=True)

        # calculate current ROI
        current_price = 1.05
        current_roi = (current_price - entry_price) / entry_price * 100

        # Create a list of dates from the first date in the vesting schedule until today
        dates = pd.date_range(start=min(vesting_schedule.keys()), end=pd.Timestamp.today(), freq='D')

        # Create an empty dataframe
        df_perc = pd.DataFrame(index=dates, columns=['current_token_amount', 'current_roi', 'current_usd_amount', 'next_vesting_date'])

        # Calculate the cumulative sum of unlocked tokens
        unlocked_tokens = 0
        unlocked_pct_tokens = 0
        # Fill in the dataframe with the calculated values
        for date in dates:
            unlocked_pct_tokens += vesting_schedule.get(date, 0)  # Add the percentage for the current date
            unlocked_tokens += (total_tokens_number * vesting_schedule.get(date, 0) / 100)
            df_perc.loc[date, 'current_token_amount'] = round(unlocked_tokens, 2)
            df_perc.loc[date, 'current_roi'] = round(current_roi, 2)
            df_perc.loc[date, 'current_usd_amount'] = round(unlocked_tokens * current_price,2)
            df_perc.loc[date, 'next_vesting_date'] = min([v for v in vesting_schedule.keys() if v > date], default='N/A')
            df_perc.loc[date, 'end_of_vesting'] = list(vesting_schedule.keys())[-1]
            df_perc.loc[date, 'unlocked_pct_tokens'] = round(unlocked_pct_tokens,2)  # Add the sum of percentages

        # Change the index to only display the date part
        df_perc.index = df_perc.index.date
        # Change the dates in the next_vesting_date column to only display the date part
        df_perc['next_vesting_date'] = df_perc['next_vesting_date'].apply(lambda x: x.date() if x != 'N/A' else 'N/A')
        
        # Add 'token_price' column from 'price' column in dfdf
        df_perc = df_perc.merge(dfdf[['price']], how='left', left_index=True, right_index=True)
        df_perc.rename(columns={'price': 'token_price'}, inplace=True)
        df_perc['ROI'] = (df_perc['token_price'] - entry_price) / entry_price * 100
        
        fig, ax = plt.subplots()
        ax.plot(df_perc.index, df_perc['unlocked_pct_tokens'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Unlocked %')
        ax.set_title('Unlocked Tokens %')
        
        fig2, ax = plt.subplots()
        ax.plot(df_perc.index, df_perc['ROI'])
        # Set the x-axis formatter to display dates in a readable format
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Display major ticks on a monthly basis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format dates as 'YYYY-MM-DD'

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Set the labels and title of the chart
        ax.set_xlabel('Date')
        ax.set_ylabel('ROI in %')
        ax.set_title('ROI in %')
        
        return df_perc, fig,fig2
    
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
                end_of_vesting = df_ilv['end_of_vesting'].iloc[-1]
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
                end_of_vesting = d['end_of_vesting'].iloc[-1]
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
                d,f = gxy()
                current_token_amount = d['current_token_amount'].iloc[-1]
                current_roi = d['current_roi'].iloc[-1]
                st.markdown(f"**Current ROI in %:** {current_roi}")
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                st.markdown(f"**Current USD amount:** {current_usd_amount}")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                st.markdown(f"**Next vesting date:** {next_vesting_date}")
                end_of_vesting = d['end_of_vesting'].iloc[-1]
                st.markdown(f"**End of vesting:** {end_of_vesting}")
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                st.markdown(f"**Unlocked % of Tokens:** {unlocked_pct_tokens}")
                st.pyplot(f)
                
            if project=='Kyve network':
                st.subheader("Kyve network token vesting schedule")
                d,f = kyve()
                current_token_amount = d['current_token_amount'].iloc[-1]
                st.markdown(f"**Current Token Amount:** {current_token_amount}")
                current_roi = d['current_roi'].iloc[-1]
                st.markdown(f"**Current ROI in %:** {current_roi}")
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                st.markdown(f"**Current USD amount:** {current_usd_amount}")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                st.markdown(f"**Next vesting date:** {next_vesting_date}")
                end_of_vesting = d['end_of_vesting'].iloc[-1]
                st.markdown(f"**End of vesting:** {end_of_vesting}")
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                st.markdown(f"**Unlocked % of Tokens:** {unlocked_pct_tokens}")
                st.pyplot(f)
              
            if project=='Mina':
                st.subheader("Mina token vesting schedule")
                d,f,f2 = mina()
                current_token_amount = d['current_token_amount'].iloc[-1]
                st.markdown(f"**Current Token Amount:** {current_token_amount}")
                current_roi = d['current_roi'].iloc[-1]
                st.markdown(f"**Current ROI in %:** {current_roi}")
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                st.markdown(f"**Current USD amount:** {current_usd_amount}")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                st.markdown(f"**Next vesting date:** {next_vesting_date}")
                end_of_vesting = d['end_of_vesting'].iloc[-1]
                st.markdown(f"**End of vesting:** {end_of_vesting}")
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                st.markdown(f"**Unlocked % of Tokens:** {unlocked_pct_tokens}")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Meta pool':
                st.subheader("Meta pool token vesting schedule")
                d,f,f2 = meta()
                current_token_amount = d['current_token_amount'].iloc[-1]
                st.markdown(f"**Current Token Amount:** {current_token_amount}")
                current_roi = d['current_roi'].iloc[-1]
                st.markdown(f"**Current ROI in %:** {current_roi}")
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                st.markdown(f"**Current USD amount:** {current_usd_amount}")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                st.markdown(f"**Next vesting date:** {next_vesting_date}")
                end_of_vesting = d['end_of_vesting'].iloc[-1]
                st.markdown(f"**End of vesting:** {end_of_vesting}")
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                st.markdown(f"**Unlocked % of Tokens:** {unlocked_pct_tokens}")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Cypher MOD':
                st.subheader("Cypher MOD token vesting schedule")
                d,f,f2 = cpr()
                current_token_amount = d['current_token_amount'].iloc[-1]
                st.markdown(f"**Current Token Amount:** {current_token_amount}")
                current_roi = d['current_roi'].iloc[-1]
                st.markdown(f"**Current ROI in %:** {current_roi}")
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                st.markdown(f"**Current USD amount:** {current_usd_amount}")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                st.markdown(f"**Next vesting date:** {next_vesting_date}")
                end_of_vesting = d['end_of_vesting'].iloc[-1]
                st.markdown(f"**End of vesting:** {end_of_vesting}")
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                st.markdown(f"**Unlocked % of Tokens:** {unlocked_pct_tokens}")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Starkware':
                st.subheader("Starkware token vesting schedule")
                d,f = stark()
                current_token_amount = d['current_token_amount'].iloc[-1]
                st.markdown(f"**Current Token Amount:** {current_token_amount}")
                current_roi = d['current_roi'].iloc[-1]
                st.markdown(f"**Current ROI in %:** {current_roi}")
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                st.markdown(f"**Current USD amount:** {current_usd_amount}")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                st.markdown(f"**Next vesting date:** {next_vesting_date}")
                end_of_vesting = d['end_of_vesting'].iloc[-1]
                st.markdown(f"**End of vesting:** {end_of_vesting}")
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                st.markdown(f"**Unlocked % of Tokens:** {unlocked_pct_tokens}")
                st.pyplot(f)
            if project=='Aurora':
                st.subheader("Aurora token vesting schedule")
                d,f,f2 = aurora()
                current_token_amount = d['current_token_amount'].iloc[-1]
                st.markdown(f"**Current Token Amount:** {current_token_amount}")
                current_roi = d['current_roi'].iloc[-1]
                st.markdown(f"**Current ROI in %:** {current_roi}")
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                st.markdown(f"**Current USD amount:** {current_usd_amount}")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                st.markdown(f"**Next vesting date:** {next_vesting_date}")
                end_of_vesting = d['end_of_vesting'].iloc[-1]
                st.markdown(f"**End of vesting:** {end_of_vesting}")
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                st.markdown(f"**Unlocked % of Tokens:** {unlocked_pct_tokens}")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Daosquare':
                st.subheader("Daosquare token vesting schedule")
                d,f,f2 = rice()
                current_token_amount = d['current_token_amount'].iloc[-1]
                st.markdown(f"**Current Token Amount:** {current_token_amount}")
                current_roi = d['current_roi'].iloc[-1]
                st.markdown(f"**Current ROI in %:** {current_roi}")
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                st.markdown(f"**Current USD amount:** {current_usd_amount}")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                st.markdown(f"**Next vesting date:** {next_vesting_date}")
                end_of_vesting = d['end_of_vesting'].iloc[-1]
                st.markdown(f"**End of vesting:** {end_of_vesting}")
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                st.markdown(f"**Unlocked % of Tokens:** {unlocked_pct_tokens}")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Burrow':
                st.subheader("Burrow token vesting schedule")
                d,f,f2 = brrr()
                current_token_amount = d['current_token_amount'].iloc[-1]
                st.markdown(f"**Current Token Amount:** {current_token_amount}")
                current_roi = d['current_roi'].iloc[-1]
                st.markdown(f"**Current ROI in %:** {current_roi}")
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                st.markdown(f"**Current USD amount:** {current_usd_amount}")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                st.markdown(f"**Next vesting date:** {next_vesting_date}")
                end_of_vesting = d['end_of_vesting'].iloc[-1]
                st.markdown(f"**End of vesting:** {end_of_vesting}")
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                st.markdown(f"**Unlocked % of Tokens:** {unlocked_pct_tokens}")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Gitcoin':
                st.subheader("Gitcoin token vesting schedule")
                d,f,f2 = gtc()
                current_token_amount = d['current_token_amount'].iloc[-1]
                st.markdown(f"**Current Token Amount:** {current_token_amount}")
                current_roi = d['current_roi'].iloc[-1]
                st.markdown(f"**Current ROI in %:** {current_roi}")
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                st.markdown(f"**Current USD amount:** {current_usd_amount}")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                st.markdown(f"**Next vesting date:** {next_vesting_date}")
                end_of_vesting = d['end_of_vesting'].iloc[-1]
                st.markdown(f"**End of vesting:** {end_of_vesting}")
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                st.markdown(f"**Unlocked % of Tokens:** {unlocked_pct_tokens}")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Treasure DAO':
                st.subheader("Treasure DAO token vesting schedule")
                d,f,f2 = magic()
                current_token_amount = d['current_token_amount'].iloc[-1]
                st.markdown(f"**Current Token Amount:** {current_token_amount}")
                current_roi = d['current_roi'].iloc[-1]
                st.markdown(f"**Current ROI in %:** {current_roi}")
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                st.markdown(f"**Current USD amount:** {current_usd_amount}")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                st.markdown(f"**Next vesting date:** {next_vesting_date}")
                end_of_vesting = d['end_of_vesting'].iloc[-1]
                st.markdown(f"**End of vesting:** {end_of_vesting}")
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                st.markdown(f"**Unlocked % of Tokens:** {unlocked_pct_tokens}")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Alethea':
                st.subheader("Alethea MOD token vesting schedule")
                d,f,f2 = ali()
                current_token_amount = d['current_token_amount'].iloc[-1]
                st.markdown(f"**Current Token Amount:** {current_token_amount}")
                current_roi = d['current_roi'].iloc[-1]
                st.markdown(f"**Current ROI in %:** {current_roi}")
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                st.markdown(f"**Current USD amount:** {current_usd_amount}")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                st.markdown(f"**Next vesting date:** {next_vesting_date}")
                end_of_vesting = d['end_of_vesting'].iloc[-1]
                st.markdown(f"**End of vesting:** {end_of_vesting}")
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                st.markdown(f"**Unlocked % of Tokens:** {unlocked_pct_tokens}")
                st.pyplot(f)
                st.pyplot(f2)
            if project=='Perion':
                st.subheader("Perion MOD token vesting schedule")
                d,f,f2 = perc()
                current_token_amount = d['current_token_amount'].iloc[-1]
                st.markdown(f"**Current Token Amount:** {current_token_amount}")
                current_roi = d['current_roi'].iloc[-1]
                st.markdown(f"**Current ROI in %:** {current_roi}")
                current_usd_amount = d['current_usd_amount'].iloc[-1]
                st.markdown(f"**Current USD amount:** {current_usd_amount}")
                next_vesting_date = d['next_vesting_date'].iloc[-1]
                st.markdown(f"**Next vesting date:** {next_vesting_date}")
                end_of_vesting = d['end_of_vesting'].iloc[-1]
                st.markdown(f"**End of vesting:** {end_of_vesting}")
                unlocked_pct_tokens = d['unlocked_pct_tokens'].iloc[-1]
                st.markdown(f"**Unlocked % of Tokens:** {unlocked_pct_tokens}")
                st.pyplot(f)
                st.pyplot(f2)
