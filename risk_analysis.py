# risk_analysis.py
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def calculate_daily_returns(price_series: pd.Series) -> pd.Series:
    return price_series.pct_change().dropna()

def calculate_volatility(price_series: pd.Series, annualize=True) -> float:
    daily_returns = calculate_daily_returns(price_series)
    vol = daily_returns.std()
    if annualize:
        vol = vol * np.sqrt(252)
    return vol * 100

def calculate_var(price_series: pd.Series, confidence_level: float = 0.95) -> float:
    daily_returns = calculate_daily_returns(price_series)
    var = daily_returns.quantile(1 - confidence_level)
    return abs(var * 100)

def calculate_correlation(series_a: pd.Series, series_b: pd.Series) -> float:
    returns_a = calculate_daily_returns(series_a)
    returns_b = calculate_daily_returns(series_b)
    aligned_returns = pd.concat([returns_a, returns_b], axis=1).dropna()
    return aligned_returns.iloc[:, 0].corr(aligned_returns.iloc[:, 1])

def detect_unusual_volume(volume_series: pd.Series, window: int = 20, threshold: float = 2.5) -> pd.Series:
    """Detecta volúmenes que superan N veces la media móvil."""
    rolling_mean = volume_series.rolling(window=window).mean()
    is_unusual = volume_series > (rolling_mean * threshold)
    return is_unusual.iloc[-1] # Devuelve si el último dato es inusual

def create_projection(price_series: pd.Series, days_to_predict: int) -> pd.DataFrame:
    """Crea una proyección de precios futuros usando regresión lineal."""
    df = price_series.reset_index()
    df['time'] = np.arange(len(df.index))

    X = df[['time']]
    y = df['price']
    
    model = LinearRegression()
    model.fit(X, y)
    
    future_time = np.arange(len(df.index), len(df.index) + days_to_predict).reshape(-1, 1)
    future_prediction = model.predict(future_time)
    
    future_dates = pd.to_datetime(pd.date_range(start=df['date'].iloc[-1], periods=days_to_predict + 1)[1:])
    
    projection_df = pd.DataFrame({'date': future_dates, 'predicted_price': future_prediction})
    return projection_df