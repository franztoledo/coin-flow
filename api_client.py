# api_client.py
import requests
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600) # Cache de 1 hora para datos que cambian con frecuencia
def get_api_data(endpoint, params=None):
    try:
        api_key = st.secrets["COINGECKO_API_KEY"]
        base_url = "https://api.coingecko.com/api/v3"
        url = f"{base_url}/{endpoint}"
        if params is None:
            params = {}
        params['x_cg_demo_api_key'] = api_key
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error de API: {e}")
        return None

def get_top_coins(limit=100):
    params = {'vs_currency': 'usd', 'order': 'market_cap_desc', 'per_page': limit, 'page': 1}
    return pd.DataFrame(get_api_data("coins/markets", params) or [])

@st.cache_data(ttl=86400)
def get_all_coins_list():
    return pd.DataFrame(get_api_data("coins/list") or [])

def get_coin_historical_data(coin_id, days=90):
    params = {'vs_currency': 'usd', 'days': str(days)}
    data = get_api_data(f"coins/{coin_id}/market_chart", params)
    if data:
        prices = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        volumes = pd.DataFrame(data['total_volumes'], columns=['timestamp', 'volume'])
        df = pd.merge(prices, volumes, on='timestamp', how='inner')
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.set_index('date')
        return df[['price', 'volume']]
    return pd.DataFrame()

def get_simple_price(ids_list):
    params = {'ids': ",".join(ids_list), 'vs_currencies': 'usd', 'include_24hr_change': 'true', 'include_24hr_vol': 'true'}
    return get_api_data("simple/price", params)