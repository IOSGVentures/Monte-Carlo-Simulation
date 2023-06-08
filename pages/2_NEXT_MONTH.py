import numpy as np
import altair as alt
import pandas as pd
import streamlit as st
import requests
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
import datetime 
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

st.set_page_config(page_title="Token Vesting for the next month", page_icon="🧐", layout="wide")
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
    st.title(":date: Token Vesting for the next month")
    st.markdown("##")
    vesting_schedule_illuvium = {pd.Timestamp('2022-07-30'):8.33, pd.Timestamp('2022-08-30'):8.33, pd.Timestamp('2022-09-30'):8.33, pd.Timestamp('2022-10-30'):8.33,
                        pd.Timestamp('2022-11-30'):8.33, pd.Timestamp('2022-12-30'):8.33,pd.Timestamp('2023-01-30'):8.33,
                        pd.Timestamp('2023-02-28'):8.33,pd.Timestamp('2023-03-30'):8.34,pd.Timestamp('2023-04-30'):8.34,pd.Timestamp('2023-05-30'):8.34,pd.Timestamp('2023-06-30'):8.34}




    vesting_schedule_arweave = {pd.Timestamp('2022-02-02'):100}

    vesting_schedule_snx = {pd.Timestamp('2021-12-02'):100}

    vesting_schedule_ata1 = {pd.Timestamp('2021-06-07'):12.5,pd.Timestamp('2021-12-07'):12.5,pd.Timestamp('2022-03-07'):12.5,pd.Timestamp('2022-06-07'):12.5,
                        pd.Timestamp('2022-09-07'):12.5,pd.Timestamp('2022-12-07'):12.5,pd.Timestamp('2023-03-07'):12.5,pd.Timestamp('2023-06-07'):12.5}

    vesting_schedule_ata2 = {pd.Timestamp('2021-06-07'):12.5,pd.Timestamp('2021-12-07'):12.5,pd.Timestamp('2022-03-07'):12.5,pd.Timestamp('2022-06-07'):12.5,pd.Timestamp('2022-09-07'):12.5,
                        pd.Timestamp('2022-12-07'):12.5,pd.Timestamp('2023-03-07'):12.5,pd.Timestamp('2023-06-07'):12.5}

    vesting_schedule_lqty = {pd.Timestamp('2022-04-05'):25,pd.Timestamp('2022-05-05'):2.77,pd.Timestamp('2022-06-05'):2.77,pd.Timestamp('2022-07-05'):2.77,pd.Timestamp('2022-08-05'):2.77,
                        pd.Timestamp('2022-09-05'):2.77,pd.Timestamp('2022-10-05'):2.77,pd.Timestamp('2022-11-05'):2.78,pd.Timestamp('2022-12-05'):2.78,pd.Timestamp('2023-01-05'):2.78,
                        pd.Timestamp('2023-02-05'):2.78,pd.Timestamp('2023-03-05'):2.78,pd.Timestamp('2023-04-05'):2.78,pd.Timestamp('2023-05-05'):2.78,pd.Timestamp('2023-06-05'):2.78,
                        pd.Timestamp('2023-07-05'):2.78,pd.Timestamp('2023-08-05'):2.78,pd.Timestamp('2023-09-05'):2.78,pd.Timestamp('2023-10-05'):2.78,pd.Timestamp('2023-11-05'):2.78,
                        pd.Timestamp('2023-12-05'):2.78,pd.Timestamp('2024-01-05'):2.78,pd.Timestamp('2024-02-05'):2.78,pd.Timestamp('2024-03-05'):2.78,pd.Timestamp('2024-04-05'):2.78,
                        pd.Timestamp('2024-05-05'):2.78,pd.Timestamp('2024-06-05'):2.78,pd.Timestamp('2024-07-05'):2.78
                        }

    vesting_schedule_coin98 = {pd.Timestamp('2022-07-23'):1.92,pd.Timestamp('2022-05-05'):2.77,pd.Timestamp('2022-06-05'):2.77,pd.Timestamp('2022-07-05'):2.77,pd.Timestamp('2022-08-05'):2.77,
                        pd.Timestamp('2022-09-05'):2.77,pd.Timestamp('2022-10-05'):2.77,pd.Timestamp('2022-11-05'):2.77,pd.Timestamp('2022-12-05'):2.77,pd.Timestamp('2023-01-05'):2.77,
                        pd.Timestamp('2023-02-05'):2.77,pd.Timestamp('2023-03-05'):2.77,pd.Timestamp('2023-04-05'):2.77,pd.Timestamp('2023-05-05'):2.77,pd.Timestamp('2023-06-05'):2.77,
                        pd.Timestamp('2023-07-05'):2.77,pd.Timestamp('2023-08-05'):2.77,pd.Timestamp('2023-09-05'):2.77,pd.Timestamp('2023-10-05'):2.77,pd.Timestamp('2023-11-05'):2.77,
                        pd.Timestamp('2023-12-05'):2.77,pd.Timestamp('2024-01-05'):2.77,pd.Timestamp('2024-02-05'):2.77,pd.Timestamp('2024-03-05'):2.77,pd.Timestamp('2024-04-05'):2.77,
                        pd.Timestamp('2024-05-05'):2.77,pd.Timestamp('2024-06-05'):2.77,pd.Timestamp('2024-07-05'):2.77,pd.Timestamp('2024-08-05'):2.77,pd.Timestamp('2024-09-05'):2.77,
                        pd.Timestamp('2024-10-05'):2.77,pd.Timestamp('2024-11-05'):2.77,pd.Timestamp('2024-12-05'):2.77,pd.Timestamp('2025-01-05'):2.77,pd.Timestamp('2025-02-05'):2.77,
                        pd.Timestamp('2025-03-05'):2.77,pd.Timestamp('2023-07-23'):2.77}

    vesting_schedule_uma = {pd.Timestamp('2021-08-31'):100}

    vesting_schedule_mcdex = {pd.Timestamp('2021-08-31'):100}

    vesting_schedule_izumi = {pd.Timestamp('2022-12-21'):100}

    vesting_schedule_insurace = {pd.Timestamp('2023-05-15'):100}

    vesting_schedule_thales = {pd.Timestamp('2022-09-16'):50,pd.Timestamp('2022-10-16'):4.17,pd.Timestamp('2022-11-16'):4.17,pd.Timestamp('2022-12-16'):4.17,pd.Timestamp('2023-01-16'):4.17,
                        pd.Timestamp('2023-02-16'):4.17,pd.Timestamp('2023-03-16'):4.17,pd.Timestamp('2023-04-16'):4.17,pd.Timestamp('2023-05-16'):4.17,pd.Timestamp('2023-06-16'):4.16,
                        pd.Timestamp('2023-07-16'):4.16,pd.Timestamp('2023-08-16'):4.16,pd.Timestamp('2023-09-16'):4.16}

    vesting_schedule_if = {pd.Timestamp('2021-06-18'):25,pd.Timestamp('2022-07-18'):6.25,pd.Timestamp('2022-08-18'):6.25,pd.Timestamp('2022-09-18'):6.25,pd.Timestamp('2022-10-18'):6.25,
                        pd.Timestamp('2022-11-18'):6.25,pd.Timestamp('2022-12-18'):6.25,pd.Timestamp('2023-01-18'):6.25,pd.Timestamp('2023-02-18'):6.25,pd.Timestamp('2023-03-18'):6.25,
                        pd.Timestamp('2023-04-18'):6.25,pd.Timestamp('2023-05-18'):6.25,pd.Timestamp('2023-06-18'):6.25}

    vesting_schedule_moonbeam = {pd.Timestamp('2023-01-11'):100}

    vesting_schedule_astar = {pd.Timestamp('2022-07-17'):100}

    vesting_schedule_ujenny = {pd.Timestamp('2021-05-16'):100}

    vesting_schedule_finnexus = {pd.Timestamp('2022-07-03'):100}

    vesting_schedule_stakewise = {pd.Timestamp('2022-06-20'):5.65,pd.Timestamp('2022-07-20'):5.55,pd.Timestamp('2022-08-20'):5.55,pd.Timestamp('2022-09-20'):5.55,
                        pd.Timestamp('2022-10-20'):5.55,pd.Timestamp('2022-11-20'):5.55,pd.Timestamp('2022-12-20'):5.55,pd.Timestamp('2023-01-20'):5.55,
                        pd.Timestamp('2023-02-20'):5.55,pd.Timestamp('2023-03-20'):5.55,pd.Timestamp('2023-04-20'):5.55,pd.Timestamp('2023-05-20'):5.55,
                        pd.Timestamp('2023-06-20'):5.55,pd.Timestamp('2023-07-20'):5.55,pd.Timestamp('2023-08-20'):5.55,pd.Timestamp('2023-09-20'):5.55,
                        pd.Timestamp('2023-10-20'):5.55,pd.Timestamp('2023-11-20'):5.55}

    vesting_schedule_centrifuge = {pd.Timestamp('2021-12-16'):50,pd.Timestamp('2022-01-16'):2.9,pd.Timestamp('2022-01-16'):2.083,pd.Timestamp('2022-02-16'):2.083,
                        pd.Timestamp('2022-03-16'):2.083,pd.Timestamp('2022-04-16'):2.083,pd.Timestamp('2022-05-16'):2.083,pd.Timestamp('2022-06-16'):2.083,
                        pd.Timestamp('2022-07-16'):2.083,pd.Timestamp('2022-08-16'):2.083,pd.Timestamp('2022-09-16'):2.083,pd.Timestamp('2022-10-16'):2.083,
                        pd.Timestamp('2022-11-16'):2.083,pd.Timestamp('2022-12-16'):2.083,pd.Timestamp('2023-01-16'):2.083,pd.Timestamp('2023-02-16'):2.083,
                        pd.Timestamp('2023-03-16'):2.083,pd.Timestamp('2023-04-16'):2.083,pd.Timestamp('2023-05-16'):2.083,pd.Timestamp('2023-06-16'):2.083,
                        pd.Timestamp('2023-07-16'):2.083,pd.Timestamp('2023-08-16'):2.083,pd.Timestamp('2023-09-16'):2.083,pd.Timestamp('2023-10-16'):2.083,
                        pd.Timestamp('2023-11-16'):2.083,pd.Timestamp('2023-12-16'):2.083}

    vesting_schedule_galaxy = {pd.Timestamp('2022-02-17'):12,pd.Timestamp('2022-05-17'):11,pd.Timestamp('2022-08-17'):11,pd.Timestamp('2022-11-17'):11,
                        pd.Timestamp('2023-02-17'):11,pd.Timestamp('2023-05-17'):11,pd.Timestamp('2023-08-17'):11,pd.Timestamp('2023-11-17'):11,
                        pd.Timestamp('2024-02-17'):11}

    vesting_schedule_kyve = {pd.Timestamp('2022-12-31'):10,pd.Timestamp('2023-01-31'):5,pd.Timestamp('2023-02-28'):5,pd.Timestamp('2023-03-31'):5,pd.Timestamp('2023-04-30'):5
                        ,pd.Timestamp('2023-05-31'):5,pd.Timestamp('2023-06-30'):5,pd.Timestamp('2023-07-31'):5,pd.Timestamp('2023-08-31'):5,pd.Timestamp('2023-09-30'):5
                        ,pd.Timestamp('2023-10-31'):5,pd.Timestamp('2023-11-30'):5,pd.Timestamp('2023-12-31'):5,pd.Timestamp('2024-01-31'):5,pd.Timestamp('2024-02-28'):5
                        ,pd.Timestamp('2024-03-31'):5,pd.Timestamp('2024-04-30'):5,pd.Timestamp('2024-05-31'):5,pd.Timestamp('2024-06-30'):5}

    vesting_schedule_mina = {pd.Timestamp('2023-02-27'):50,pd.Timestamp('2024-02-27'):2.9}

    vesting_schedule_meta = {pd.Timestamp('2023-05-26'):100/12,pd.Timestamp('2023-06-26'):100/12,pd.Timestamp('2023-07-26'):100/12,
                             pd.Timestamp('2023-08-26'):100/12,pd.Timestamp('2023-09-26'):100/12,pd.Timestamp('2023-10-26'):100/12,
                             pd.Timestamp('2023-11-26'):100/12,pd.Timestamp('2023-12-26'):100/12,pd.Timestamp('2024-01-26'):100/12,
                             pd.Timestamp('2024-02-26'):100/12,pd.Timestamp('2024-03-26'):100/12,pd.Timestamp('2024-04-26'):100/12,}

    vesting_schedule_cypher = {pd.Timestamp('2022-09-01'):20,pd.Timestamp('2022-12-01'):10,pd.Timestamp('2023-03-01'):10,
                        pd.Timestamp('2023-06-01'):10,pd.Timestamp('2023-09-01'):10,pd.Timestamp('2023-12-01'):10,
                        pd.Timestamp('2024-03-01'):10,pd.Timestamp('2024-06-01'):10,pd.Timestamp('2024-09-01'):10}

    vesting_schedule_stark = {pd.Timestamp('2022-11-01'):25,pd.Timestamp('2022-12-01'):2.083,pd.Timestamp('2023-01-01'):2.083,
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

    vesting_schedule_aurora = {pd.Timestamp('2022-05-18'):3.25,pd.Timestamp('2022-08-18'):3.25,pd.Timestamp('2022-11-18'):3.5,
                        pd.Timestamp('2023-02-18'):10,pd.Timestamp('2023-05-18'):10,pd.Timestamp('2023-08-18'):10,
                        pd.Timestamp('2023-11-18'):10,pd.Timestamp('2024-02-18'):10,pd.Timestamp('2024-05-18'):10,
                        pd.Timestamp('2024-08-18'):10,pd.Timestamp('2024-11-18'):10,pd.Timestamp('2025-02-18'):10}

    vesting_schedule_daosquare = {pd.Timestamp('2022-07-16'):10,pd.Timestamp('2022-10-16'):10,
                        pd.Timestamp('2023-01-16'):10,pd.Timestamp('2023-04-16'):10,pd.Timestamp('2023-07-16'):10,
                        pd.Timestamp('2023-10-16'):10,pd.Timestamp('2024-01-16'):10,pd.Timestamp('2024-04-16'):10,
                        pd.Timestamp('2024-07-16'):10,pd.Timestamp('2024-10-16'):10}

    vesting_schedule_burrow = {pd.Timestamp('2022-12-15'):50,pd.Timestamp('2023-01-15'):50/12,
                        pd.Timestamp('2023-02-15'):50/12,pd.Timestamp('2023-03-15'):50/12,pd.Timestamp('2023-04-15'):50/12,
                        pd.Timestamp('2023-05-15'):50/12,pd.Timestamp('2023-06-15'):50/12,pd.Timestamp('2023-07-15'):50/12,
                        pd.Timestamp('2023-08-15'):50/12,pd.Timestamp('2023-09-15'):50/12,pd.Timestamp('2023-10-15'):50/12,
                        pd.Timestamp('2023-11-15'):50/12,pd.Timestamp('2023-12-15'):50/12}

    vesting_schedule_gitcoin = {pd.Timestamp('2023-11-01'):100/12,pd.Timestamp('2023-12-01'):100/12,pd.Timestamp('2024-01-01'):100/12,
                        pd.Timestamp('2024-02-01'):100/12,pd.Timestamp('2024-03-01'):100/12,pd.Timestamp('2024-04-01'):100/12,
                        pd.Timestamp('2024-05-01'):100/12,pd.Timestamp('2024-06-01'):100/12,pd.Timestamp('2024-07-01'):100/12,
                        pd.Timestamp('2024-08-01'):100/12,pd.Timestamp('2024-09-01'):100/12,pd.Timestamp('2024-10-01'):100/12}

    vesting_schedule_treasuredao = {pd.Timestamp('2023-11-18'):100/24,pd.Timestamp('2023-12-18'):100/24,pd.Timestamp('2024-01-18'):100/24,
                        pd.Timestamp('2024-02-18'):100/24,pd.Timestamp('2024-03-18'):100/24,pd.Timestamp('2024-04-18'):100/24,
                        pd.Timestamp('2024-05-18'):100/24,pd.Timestamp('2024-06-18'):100/24,pd.Timestamp('2024-07-18'):100/24,
                        pd.Timestamp('2024-08-18'):100/24,pd.Timestamp('2024-09-18'):100/24,pd.Timestamp('2024-10-18'):100/24,
                        pd.Timestamp('2024-11-18'):100/24,pd.Timestamp('2024-12-18'):100/24,pd.Timestamp('2025-01-18'):100/24,
                        pd.Timestamp('2025-02-18'):100/24,pd.Timestamp('2025-03-18'):100/24,pd.Timestamp('2025-04-18'):100/24,
                        pd.Timestamp('2025-05-18'):100/24,pd.Timestamp('2025-06-18'):100/24,pd.Timestamp('2025-07-18'):100/24,
                        pd.Timestamp('2025-08-18'):100/24,pd.Timestamp('2025-09-18'):100/24,pd.Timestamp('2025-10-18'):100/24,
                        }

    vesting_schedule_alethea = {pd.Timestamp('2023-11-18'):100/24,pd.Timestamp('2023-12-18'):100/24,pd.Timestamp('2024-01-18'):100/24,
                        pd.Timestamp('2024-02-18'):100/24,pd.Timestamp('2024-03-18'):100/24,pd.Timestamp('2024-04-18'):100/24,
                        pd.Timestamp('2024-05-18'):100/24,pd.Timestamp('2024-06-18'):100/24,pd.Timestamp('2024-07-18'):100/24,
                        pd.Timestamp('2024-08-18'):100/24,pd.Timestamp('2024-09-18'):100/24,pd.Timestamp('2024-10-18'):100/24,
                        pd.Timestamp('2024-11-18'):100/24,pd.Timestamp('2024-12-18'):100/24,pd.Timestamp('2025-01-18'):100/24,
                        pd.Timestamp('2025-02-18'):100/24,pd.Timestamp('2025-03-18'):100/24,pd.Timestamp('2025-04-18'):100/24,
                        pd.Timestamp('2025-05-18'):100/24,pd.Timestamp('2025-06-18'):100/24,pd.Timestamp('2025-07-18'):100/24,
                        pd.Timestamp('2025-08-18'):100/24,pd.Timestamp('2025-09-18'):100/24,pd.Timestamp('2025-10-18'):100/24,
                        }

    vesting_schedule_perion = {pd.Timestamp('2022-02-06'):10,pd.Timestamp('2023-02-03'):90/12,pd.Timestamp('2023-03-03'):90/12,
                        pd.Timestamp('2023-04-03'):90/12,pd.Timestamp('2023-05-03'):90/12,pd.Timestamp('2023-06-03'):90/12,
                        pd.Timestamp('2023-07-03'):90/12,pd.Timestamp('2023-08-03'):90/12,pd.Timestamp('2023-09-03'):90/12,
                        pd.Timestamp('2023-10-03'):90/12,pd.Timestamp('2023-11-03'):90/12,pd.Timestamp('2023-12-03'):90/12,
                        pd.Timestamp('2024-01-03'):90/12,pd.Timestamp('2024-02-03'):100/12,
                        }

    vesting_schedules = {'Illuvium': vesting_schedule_illuvium,
                         'Arweave': vesting_schedule_arweave,
                         'Synthetix': vesting_schedule_snx,
                         'Automata 1': vesting_schedule_ata1,
                         'Automata 2': vesting_schedule_ata2,
                         'Liquity': vesting_schedule_lqty,
                         'Coin98': vesting_schedule_coin98,
                         'Uma': vesting_schedule_uma,
                         'Mcdex': vesting_schedule_mcdex,
                         'Izumi': vesting_schedule_izumi,
                         'Insurace': vesting_schedule_insurace,
                         'Thales': vesting_schedule_thales,
                         'Impossible finance': vesting_schedule_if,
                         'Moonbeam': vesting_schedule_moonbeam,
                         'Astar': vesting_schedule_astar,
                         'Ujenny': vesting_schedule_ujenny,
                         'Finnexus': vesting_schedule_finnexus,
                         'Stakewise': vesting_schedule_stakewise,
                         'Centrifuge': vesting_schedule_centrifuge,
                         'Galaxy':vesting_schedule_galaxy,
                         'Kyve network': vesting_schedule_kyve,
                         'Mina': vesting_schedule_mina,
                         'Meta Pool': vesting_schedule_meta,
                         'Cypher': vesting_schedule_cypher,
                         'Starkware': vesting_schedule_stark,
                         'Aurora': vesting_schedule_aurora,
                         'Daosquare': vesting_schedule_daosquare,
                         'Burrow': vesting_schedule_burrow,
                         'Gitcoin': vesting_schedule_gitcoin,
                         'Treasure DAO': vesting_schedule_treasuredao,
                         'Alethea': vesting_schedule_alethea,
                         'Perion': vesting_schedule_perion}
    total_tokens =      {'Illuvium': 66666.67,
                         'Arweave': 250000,
                         'Synthetix': 241936,
                         'Automata 1': 4800000,
                         'Automata 2': 3750000,
                         'Liquity': 357143,
                         'Coin98': 2666667,
                         'Uma': 101678.70,
                         'Mcdex': 20000,
                         'Izumi': 16150000,
                         'Insurace': 228571.43,
                         'Thales': 303030.00,
                         'Impossible finance': 1666666.67,
                         'Moonbeam': 5000000.00,
                         'Astar': 19366666.00,
                         'Ujenny': 148699,
                         'Finnexus': 1250000.00,
                         'Stakewise': 3333333.33,
                         'Centrifuge': 1666666.67,
                         'Galaxy': 1333333.33,
                         'Kyve network': 5000000,
                         'Mina': 537634,
                         'Meta Pool': 1000000000,
                         'Cypher': 54000000,
                         'Starkware': 96318,
                         'Aurora': 1000000,
                         'Daosquare': 370370.00 ,
                         'Burrow': 2000000,
                         'Gitcoin': 468750,
                         'Treasure DAO': 869293,
                         'Alethea': 25000000.00,
                         'Perion': 1000000}
    # Determine the earliest month among all projects
    earliest_month = min(min(vesting_schedules[project].keys()) for project in vesting_schedules)

    # Create a list of months from the earliest month to the maximum unlock date
    max_date = max(max(vesting_schedules[project].keys()) for project in vesting_schedules)
    months = pd.date_range(start=earliest_month, end=max_date, freq='M')

    # Create an empty dataframe with months as rows and project names as columns
    df = pd.DataFrame(index=months.strftime('%Y-%m'), columns=vesting_schedules.keys())

    # Populate the dataframe with the unlock percentages for each month and project
    for project, vesting_schedule in vesting_schedules.items():
        for date, percentage in vesting_schedule.items():
            month = pd.to_datetime(date).to_period('M')
            df.loc[month.strftime('%Y-%m'), project] = percentage

    # Fill any missing values in the dataframe (if any) with 0
    df = df.fillna(0)

    # Get the start and end of the next month
    next_month_start = pd.Timestamp.today().to_period('M').to_timestamp(how='start') + pd.offsets.MonthBegin(1)
    next_month_end = pd.Timestamp.today().to_period('M').to_timestamp(how='end') + pd.offsets.MonthEnd(1)

    # Convert the index to a DatetimeIndex
    df.index = pd.to_datetime(df.index)

    # Filter the DataFrame to get the next month's expected unlocked tokens
    next_month_unlocked = df[(df.index >= next_month_start) & (df.index <= next_month_end)]

    # Set up the Streamlit application
    st.write("Expected Unlocked Tokens Next Month")

    # Display the expected unlocked tokens for each project
    if next_month_unlocked.empty:
        st.write("No data available for the next month.")
    else:
        for column in next_month_unlocked.columns:
            percentage = next_month_unlocked[column][0]
            if percentage > 0:
                unlocked_tokens = round(percentage * total_tokens[column] / 100)
                st.write(f"{column}: {round(percentage,2)}% ({unlocked_tokens} tokens)")

