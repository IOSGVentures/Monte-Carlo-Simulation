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

st.set_page_config(page_title="Multiples table", page_icon="🧐", layout="wide")
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
    st.title(":earth_asia: Multiples table")
    st.markdown("##")
    def multi_project_df2(project_ids):
        """
        This function retrieves metrics data for multiple cryptocurrency projects from an API and
        creates a dataframe with various financial metrics for each project.
        It takes a list of project_ids as input and returns a pandas dataframe with financial metrics such as:
        daily average volume, annualized volume, annualized fees, annualized revenue,
        TVL (Total Value Locked), TVL turnover, token price, realized volatility, market cap (MC),
        fully diluted valuation (FDV), MC/AF, FDV/AF, MC/AR, FDV/AR, MC/TVL, and FDV/TVL.
    
        To use this function, import it into your python script and call it with a list of project_ids as an argument.
        The resulting dataframe can be used for financial analysis and comparisons between different projects.
    
        Example usage:
    
        from multi_project_df import multi_project_df
        project_ids = ['bitcoin', 'ethereum']
        result = multi_project_df(project_ids)
        """
    
        def get_data(data):
            date = []
            price = []
            FDV  =[]
            volume = []
            fees  = []
            revenue  = []
            TVL = []
            MCAP  = []
            earnings = []
            active_developers = []
            code_commits = []
            for i in range(len(data)):
                date.append(pd.to_datetime((data[i]['timestamp'])))
                price.append(data[i]['price'])
                FDV.append(data[i]['market_cap_fully_diluted'])
                volume.append(data[i]['token_trading_volume'])
                fees.append(data[i]['fees'])
                revenue.append(data[i]['revenue'])
                TVL.append(data[i]['tvl'])
                MCAP.append(data[i]['market_cap_circulating'])
                earnings.append(data[i]['earnings'])
                active_developers.append(data[i]['active_developers'])
                code_commits.append(data[i]['code_commits'])
            dataa = [price,FDV,volume,fees,revenue,TVL,MCAP,earnings,active_developers,code_commits]
            df = pd.DataFrame(dataa, columns=date, index=['Price','FDV','Volume','Fees','Revenue','TVL','MCAP','earnings','active_developers','code_commits'])
            df = df.T.dropna()
            return df
    
        def get_data_btc(data):
            date = []
            price = []
            FDV  =[]
            volume = []
            fees  = []
            revenue  = []
            #TVL = []
            MCAP  = []
            earnings = []
            active_developers = []
            code_commits = []
            for i in range(len(data)):
                date.append(pd.to_datetime((data[i]['timestamp'])))
                price.append(data[i]['price'])
                FDV.append(data[i]['market_cap_fully_diluted'])
                volume.append(data[i]['token_trading_volume'])
                fees.append(data[i]['fees'])
                revenue.append(data[i]['revenue'])
                #TVL.append(data[i]['tvl'])
                MCAP.append(data[i]['market_cap_circulating'])
                earnings.append(data[i]['earnings'])
                active_developers.append(data[i]['active_developers'])
                code_commits.append(data[i]['code_commits'])
            dataa = [price,FDV,volume,fees,revenue,MCAP,earnings,active_developers,code_commits]
            df = pd.DataFrame(dataa, columns=date, index=['Price','FDV','Volume','Fees','Revenue','MCAP','earnings','active_developers','code_commits'])
            df = df.T.dropna()
            return df
    
        def get_data_m(data):
            date = []
            price = []
            FDV  =[]
            volume = []
            fees  = []
            revenue  = []
            TVL = []
            MCAP  = []
            earnings = []
            active_developers = []
            code_commits = []
            for i in range(len(data)):
                date.append(pd.to_datetime((data[i]['timestamp'])))
                price.append(data[i]['price'])
                FDV.append(data[i]['market_cap_fully_diluted'])
                volume.append(data[i]['token_trading_volume'])
                fees.append(data[i]['fees'])
                revenue.append(data[i]['revenue'])
                TVL.append(data[i]['tvl'])
                MCAP.append(data[i]['market_cap_fully_diluted'])
                earnings.append(data[i]['earnings'])
                active_developers.append(data[i]['active_developers'])
                code_commits.append(data[i]['code_commits'])
            dataa = [price,FDV,volume,fees,revenue,TVL,MCAP,earnings,active_developers,code_commits]
            df = pd.DataFrame(dataa, columns=date, index=['Price','FDV','Volume','Fees','Revenue','TVL','MCAP','earnings','active_developers','code_commits'])
            df = df.T.dropna()
            return df
        def get_data_c(data):
            date = []
            price = []
            FDV  =[]
            volume = []
            TVL = []
            MCAP  = []
            earnings = []
            active_developers = []
            code_commits = []
            for i in range(len(data)):
                date.append(pd.to_datetime((data[i]['timestamp'])))
                price.append(data[i]['price'])
                FDV.append(data[i]['market_cap_fully_diluted'])
                volume.append(data[i]['token_trading_volume'])
                TVL.append(data[i]['tvl'])
                MCAP.append(data[i]['market_cap_circulating'])
                earnings.append(data[i]['earnings'])
                active_developers.append(data[i]['active_developers'])
                code_commits.append(data[i]['code_commits'])
            dataa = [price,FDV,volume,TVL,MCAP,earnings,active_developers,code_commits]
            df = pd.DataFrame(dataa, columns=date, index=['Price','FDV','Volume','TVL','MCAP','earnings','active_developers','code_commits'])
            df = df.T.dropna()
            return df
        url_c = 'https://api.llama.fi/summary/fees/curve-finance?dataType=dailyFees'
        r_c = requests.get(url_c)
        data_c = r_c.json()
        d_c = data_c['totalDataChart']
        df_c = pd.DataFrame(d_c, columns=['date', 'fees'])
        df_c['date'] = pd.to_datetime(df_c['date'], unit='s')
        df_c.set_index('date', inplace=True)
        df_c['revenue'] = df_c['fees']/2
    
    
        df_list = []
        for project_id in project_ids:
            if project_id in ('makerdao','radiant-capital'):
              url1 = f"https://api.tokenterminal.com/v2/projects/{project_id}/metrics"
              headers = {"Authorization": "Bearer 3365c8fd-ade3-410f-99e4-9c82d9831f0b"}
              response1 = requests.get(url1, headers=headers)
              data_shows1 = json.loads(response1.text)
              data1 = data_shows1['data']
              d1 = get_data_m(data1)
              d1 = d1[::-1]
    
              d1['RETURN'] = (d1['Price']/d1['Price'].shift(1)) - 1
    
              volume, tvl, price, fee, revenue, mcap, mcapfd, earnings, active_developers, code_commits = d1['Volume'],d1['TVL'], d1['Price'], d1['Fees'], d1['Revenue'], d1['MCAP'], d1['FDV'], d1['earnings'], d1['active_developers'],d1['code_commits']
    
              daily_avg_volume = volume[-30:].mean()
              annualized_volume = daily_avg_volume * 365
    
              daily_avg_fees = fee[-30:].mean()
              annualized_fees = daily_avg_fees * 365
    
              daily_avg_revenue = revenue[-30:].mean()
              annualized_revenue = daily_avg_revenue * 365
    
              earnings_365d = earnings[-365:].sum()
    
              tvl_current = tvl[-1]
              tvl_turnover = volume[-30:].sum() / tvl[-30:].mean()
              token_price = price[-1]
              realized_volatility = np.std(price[-30:]) * np.sqrt(365) * 100
              mc = mcap[-1]
              fdv = mcapfd[-1]
              act_dev = active_developers[-1]
              c_commits = code_commits[-1]
    
              price_earnings = token_price/earnings[-30:].mean()
              price_fees = token_price/fee[-30:].mean()
              price_revenue = token_price/revenue[-30:].mean()
              volume_tvl = annualized_volume/tvl_current
              mc_fdv = mc/fdv
              mc_af = mc/annualized_fees
              fdv_af = fdv/annualized_fees
              mc_ar = mc/annualized_revenue
              fdv_ar = fdv/annualized_revenue
              mc_tvl = mc/tvl_current
              fdv_tvl = fdv/tvl_current
    
              titles = ['Token Price','MC ($M)','FDV ($M)','TVL ($M)','Daily Average Volume', 'Annualized Volume', 'Annualized Fees (AF)',
              'Annualized Revenue (AR)','Earnings 365D','TVL Turnover ' + str(30) + ' days', 'Realized Volatility %', 'Price/Earnings', 'Price/Fees', 'Price/Revenue', 'Volume/TVL','MC/FDV',
                    'MC / AF', 'FDV / AF', 'MC / AR', 'FDV / AR',
                    'MC / TVL', 'FDV / TVL', 'Active dev', 'Code commits']
              data = [token_price,mc,fdv,tvl_current,daily_avg_volume, annualized_volume, annualized_fees,
                  annualized_revenue, earnings_365d, tvl_turnover, realized_volatility,price_earnings,price_fees,price_revenue,volume_tvl,mc_fdv,
                  mc_af, fdv_af, mc_ar, fdv_ar, mc_tvl, fdv_tvl, act_dev, c_commits]
              table = pd.DataFrame(data = data, index = titles, columns=[f'{project_id}'])
              table.loc[:, f"{project_id}"] =table[f"{project_id}"].map('{:,.4f}'.format)
              df_list.append(table)
            elif project_id in ('uniswap'):
              url1 = f"https://api.tokenterminal.com/v2/projects/{project_id}/metrics"
              headers = {"Authorization": "Bearer 3365c8fd-ade3-410f-99e4-9c82d9831f0b"}
              response1 = requests.get(url1, headers=headers)
              data_shows1 = json.loads(response1.text)
              data1 = data_shows1['data']
              d1 = get_data_m(data1)
              d1 = d1[::-1]
              url_uni = 'https://api.coingecko.com/api/v3/coins/uniswap/market_chart?vs_currency=usd&days=1&interval=daily'
              r_uni = requests.get(url_uni)
              data_uni = r_uni.json()
              d_uni = data_uni['market_caps']
              df_uni = pd.DataFrame(d_uni, columns=['date', 'market_caps'])
              df_uni['date'] = pd.to_datetime(df_uni['date'])
              df_uni.set_index('date', inplace=True)
              mcap_uni = df_uni['market_caps'][-1]
    
              d1['RETURN'] = (d1['Price']/d1['Price'].shift(1)) - 1
    
              volume, tvl, price, fee, revenue, mcap, mcapfd, active_developers, code_commits = d1['Volume'],d1['TVL'], d1['Price'], d1['Fees'], d1['Revenue'], mcap_uni, d1['FDV'], d1['active_developers'],d1['code_commits']
              earnings = revenue
              daily_avg_volume = volume[-30:].mean()
              annualized_volume = daily_avg_volume * 365
    
              daily_avg_fees = fee[-30:].mean()
              annualized_fees = daily_avg_fees * 365
    
              daily_avg_revenue = revenue[-30:].mean()
              annualized_revenue = daily_avg_revenue * 365
              earnings_365d = earnings[-365:].sum()
    
              tvl_current = tvl[-1]
              tvl_turnover = volume[-30:].sum() / tvl[-30:].mean()
              token_price = price[-1]
              realized_volatility = np.std(price[-30:]) * np.sqrt(365) * 100
              mc = mcap
              fdv = mcapfd[-1]
              act_dev = active_developers[-1]
              c_commits = code_commits[-1]
    
              price_earnings = token_price/earnings[-30:].mean()
              price_fees = token_price/fee[-30:].mean()
              price_revenue = token_price/revenue[-30:].mean()
              volume_tvl = annualized_volume/tvl_current
              mc_fdv = mc/fdv
              mc_af = mc/annualized_fees
              fdv_af = fdv/annualized_fees
              mc_ar = mc/annualized_revenue
              fdv_ar = fdv/annualized_revenue
              mc_tvl = mc/tvl_current
              fdv_tvl = fdv/tvl_current
    
              titles = ['Token Price','MC ($M)','FDV ($M)','TVL ($M)','Daily Average Volume', 'Annualized Volume', 'Annualized Fees (AF)',
              'Annualized Revenue (AR)','Earnings 365D','TVL Turnover ' + str(30) + ' days', 'Realized Volatility %', 'Price/Earnings', 'Price/Fees', 'Price/Revenue', 'Volume/TVL','MC/FDV',
                    'MC / AF', 'FDV / AF', 'MC / AR', 'FDV / AR',
                    'MC / TVL', 'FDV / TVL', 'Active dev', 'Code commits']
              data = [token_price,mc,fdv,tvl_current,daily_avg_volume, annualized_volume, annualized_fees,
                  annualized_revenue, earnings_365d, tvl_turnover, realized_volatility,price_earnings,price_fees,price_revenue,volume_tvl,mc_fdv,
                  mc_af, fdv_af, mc_ar, fdv_ar, mc_tvl, fdv_tvl, act_dev, c_commits]
              table = pd.DataFrame(data = data, index = titles, columns=[f'{project_id}'])
              table.loc[:, f"{project_id}"] =table[f"{project_id}"].map('{:,.4f}'.format)
              df_list.append(table)
            elif project_id in ('bitcoin','ethereum'):
              url1 = f"https://api.tokenterminal.com/v2/projects/{project_id}/metrics"
              headers = {"Authorization": "Bearer 3365c8fd-ade3-410f-99e4-9c82d9831f0b"}
              response1 = requests.get(url1, headers=headers)
              data_shows1 = json.loads(response1.text)
              data1 = data_shows1['data']
              d1 = get_data_btc(data1)
              d1 = d1[::-1]
    
              d1['RETURN'] = (d1['Price']/d1['Price'].shift(1)) - 1
    
              volume, price, fee, revenue, mcap, mcapfd, earnings, active_developers, code_commits = d1['Volume'], d1['Price'], d1['Fees'], d1['Revenue'], d1['MCAP'], d1['FDV'], d1['earnings'], d1['active_developers'],d1['code_commits']
    
              daily_avg_volume = volume[-30:].mean()
              annualized_volume = daily_avg_volume * 365
    
              daily_avg_fees = fee[-30:].mean()
              annualized_fees = daily_avg_fees * 365
    
              daily_avg_revenue = revenue[-30:].mean()
              annualized_revenue = daily_avg_revenue * 365
              earnings_365d = earnings[-365:].sum()
              tvl_current = 'N/A'
              tvl_turnover = 'N/A'
              token_price = price[-1]
              realized_volatility = np.std(price[-30:]) * np.sqrt(365) * 100
              mc = mcap[-1]
              fdv = mcapfd[-1]
              act_dev = active_developers[-1]
              c_commits = code_commits[-1]
              price_earnings = token_price/earnings[-30:].mean()
              price_fees = token_price/fee[-30:].mean()
              price_revenue = token_price/revenue[-30:].mean()
              volume_tvl = 'N/A'
              mc_fdv = mc/fdv
              mc_af = mc/annualized_fees
              fdv_af = fdv/annualized_fees
              mc_ar = mc/annualized_revenue
              fdv_ar = fdv/annualized_revenue
              mc_tvl = 'N/A'
              fdv_tvl = 'N/A'
    
              titles = ['Token Price','MC ($M)','FDV ($M)','TVL ($M)','Daily Average Volume', 'Annualized Volume', 'Annualized Fees (AF)',
              'Annualized Revenue (AR)','Earnings 365D','TVL Turnover ' + str(30) + ' days', 'Realized Volatility %', 'Price/Earnings', 'Price/Fees', 'Price/Revenue', 'Volume/TVL','MC/FDV',
                    'MC / AF', 'FDV / AF', 'MC / AR', 'FDV / AR',
                    'MC / TVL', 'FDV / TVL', 'Active dev', 'Code commits']
              data = [token_price,mc,fdv,tvl_current,daily_avg_volume, annualized_volume, annualized_fees,
                  annualized_revenue, earnings_365d, tvl_turnover, realized_volatility,price_earnings,price_fees,price_revenue,volume_tvl,mc_fdv,
                  mc_af, fdv_af, mc_ar, fdv_ar, mc_tvl, fdv_tvl, act_dev, c_commits]
              table = pd.DataFrame(data = data, index = titles, columns=[f'{project_id}'])
              # Rows to format
              rows_to_format = ['Daily Average Volume', 'Annualized Volume', 'Annualized Fees (AF)',
                                'Annualized Revenue (AR)','Earnings 365D', 'Token Price', 'Realized Volatility %',
                                'MC ($M)', 'FDV ($M)','Price/Earnings', 'Price/Fees', 'Price/Revenue','MC/FDV',
                                'MC / AF', 'FDV / AF', 'MC / AR', 'FDV / AR']
    
              # Function to format the value
              format_value = lambda val: '{:,.4f}'.format(val) if isinstance(val, (int, float)) else val
    
              # Apply the formatting to the selected rows and the specific column 'project_id'
              table.loc[rows_to_format, project_id] = table.loc[rows_to_format, project_id].apply(format_value)
              df_list.append(table)
            elif project_id=='curve':
              url1 = f"https://api.tokenterminal.com/v2/projects/{project_id}/metrics"
              headers = {"Authorization": "Bearer 3365c8fd-ade3-410f-99e4-9c82d9831f0b"}
              response1 = requests.get(url1, headers=headers)
              data_shows1 = json.loads(response1.text)
              data1 = data_shows1['data']
              d1 = get_data_c(data1)
              d1 = d1[::-1]
    
              d1['RETURN'] = (d1['Price']/d1['Price'].shift(1)) - 1
    
              volume, tvl, price, fee, revenue, mcap, mcapfd, earnings, active_developers, code_commits = d1['Volume'],d1['TVL'], d1['Price'], df_c['fees'], df_c['revenue'], d1['MCAP'], d1['FDV'], d1['earnings'], d1['active_developers'],d1['code_commits']
    
              daily_avg_volume = volume[-30:].mean()
              annualized_volume = daily_avg_volume * 365
    
              daily_avg_fees = fee[-30:].mean()
              annualized_fees = daily_avg_fees * 365
    
              daily_avg_revenue = revenue[-30:].mean()
              annualized_revenue = daily_avg_revenue * 365
              earnings_365d = earnings[-365:].sum()
    
              tvl_current = tvl[-1]
              tvl_turnover = volume[-30:].sum() / tvl[-30:].mean()
              token_price = price[-1]
              realized_volatility = np.std(price[-30:]) * np.sqrt(365) * 100
              mc = mcap[-1]
              fdv = mcapfd[-1]
              act_dev = active_developers[-1]
              c_commits = code_commits[-1]
              price_earnings = token_price/earnings[-30:].mean()
              price_fees = token_price/fee[-30:].mean()
              price_revenue = token_price/revenue[-30:].mean()
              volume_tvl = annualized_volume/tvl_current
              mc_fdv = mc/fdv
              mc_af = mc/annualized_fees
              fdv_af = fdv/annualized_fees
              mc_ar = mc/annualized_revenue
              fdv_ar = fdv/annualized_revenue
              mc_tvl = mc/tvl_current
              fdv_tvl = fdv/tvl_current
    
              titles = ['Token Price','MC ($M)','FDV ($M)','TVL ($M)','Daily Average Volume', 'Annualized Volume', 'Annualized Fees (AF)',
              'Annualized Revenue (AR)','Earnings 365D','TVL Turnover ' + str(30) + ' days', 'Realized Volatility %', 'Price/Earnings', 'Price/Fees', 'Price/Revenue', 'Volume/TVL','MC/FDV',
                    'MC / AF', 'FDV / AF', 'MC / AR', 'FDV / AR',
                    'MC / TVL', 'FDV / TVL', 'Active dev', 'Code commits']
              data = [token_price,mc,fdv,tvl_current,daily_avg_volume, annualized_volume, annualized_fees,
                  annualized_revenue, earnings_365d, tvl_turnover, realized_volatility,price_earnings,price_fees,price_revenue,volume_tvl,mc_fdv,
                  mc_af, fdv_af, mc_ar, fdv_ar, mc_tvl, fdv_tvl, act_dev, c_commits]
              table = pd.DataFrame(data = data, index = titles, columns=[f'{project_id}'])
              table.loc[:, f"{project_id}"] =table[f"{project_id}"].map('{:,.4f}'.format)
              df_list.append(table)
    
            else:
              url1 = f"https://api.tokenterminal.com/v2/projects/{project_id}/metrics"
              headers = {"Authorization": "Bearer 3365c8fd-ade3-410f-99e4-9c82d9831f0b"}
              response1 = requests.get(url1, headers=headers)
              data_shows1 = json.loads(response1.text)
              data1 = data_shows1['data']
              d1 = get_data(data1)
              d1 = d1[::-1]
    
              d1['RETURN'] = (d1['Price']/d1['Price'].shift(1)) - 1
    
              volume, tvl, price, fee, revenue, mcap, mcapfd, earnings, active_developers, code_commits = d1['Volume'],d1['TVL'], d1['Price'], d1['Fees'], d1['Revenue'], d1['MCAP'], d1['FDV'], d1['earnings'], d1['active_developers'],d1['code_commits']
    
              daily_avg_volume = volume[-30:].mean()
              annualized_volume = daily_avg_volume * 365
    
              daily_avg_fees = fee[-30:].mean()
              annualized_fees = daily_avg_fees * 365
    
              daily_avg_revenue = revenue[-30:].mean()
              annualized_revenue = daily_avg_revenue * 365
              earnings_365d = earnings[-365:].sum()
    
              tvl_current = tvl[-1]
              tvl_turnover = volume[-30:].sum() / tvl[-30:].mean()
              token_price = price[-1]
              realized_volatility = np.std(price[-30:]) * np.sqrt(365) * 100
              mc = mcap[-1]
              fdv = mcapfd[-1]
              act_dev = active_developers[-30:].mean()
              c_commits = code_commits[-30:].mean()
              price_earnings = token_price/earnings[-30:].mean()
              price_fees = token_price/fee[-30:].mean()
              price_revenue = token_price/revenue[-30:].mean()
              volume_tvl = annualized_volume/tvl_current
              mc_fdv = mc/fdv
              mc_af = mc/annualized_fees
              fdv_af = fdv/annualized_fees
              mc_ar = mc/annualized_revenue
              fdv_ar = fdv/annualized_revenue
              mc_tvl = mc/tvl_current
              fdv_tvl = fdv/tvl_current
    
              titles = ['Token Price','MC ($M)','FDV ($M)','TVL ($M)','Daily Average Volume ($M)', 'Annualized Volume ($M)', 'Annualized Fees ($M)',
              'Annualized Revenue ($M)','Earnings 365D','TVL Turnover ' + str(30) + ' days', 'Realized Volatility %', 'Price/Earnings', 'Price/Fees', 'Price/Revenue', 'Volume/TVL','MC / FDV',
                    'MC / AF', 'FDV / AF', 'MC / AR', 'FDV / AR',
                    'MC / TVL', 'FDV / TVL', 'Active dev (avg 30D)', 'Code commits (avg 30D)']
              data = [token_price,mc/1e6,fdv/1e6,tvl_current/1e6,daily_avg_volume/1e6, annualized_volume/1e6, annualized_fees/1e6,
                  annualized_revenue/1e6, earnings_365d, tvl_turnover, realized_volatility,price_earnings,price_fees,price_revenue,volume_tvl,mc_fdv,
                  mc_af, fdv_af, mc_ar, fdv_ar, mc_tvl, fdv_tvl, act_dev, c_commits]
              table = pd.DataFrame(data = data, index = titles, columns=[f'{project_id}'])
              table.loc[:, f"{project_id}"] =table[f"{project_id}"].map('{:,.6f}'.format)
              df_list.append(table)
        result = pd.concat(df_list, axis=1)
        return result

    	
#with st.form("my_form",clear_on_submit=False):
    
project_ids = st.text_input('Enter the projects ID from Token Terminal', key='1')
project_ids_list = [token.strip() for token in project_ids.split(',')]

with st.form("monte_carlo_form"):
    if st.form_submit_button("Submit"):
        st.header(f"Here's table with multiples for listed projects!")
        table = multi_project_df2(project_ids_list)
        
        st.dataframe(table, use_container_width=True)
