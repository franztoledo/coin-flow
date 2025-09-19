# Trading_Desk.py
import streamlit as st
import pandas as pd
import api_client
import risk_analysis

st.set_page_config(page_title="Trading Desk", page_icon="📈", layout="wide")

st.title("Trading Desk: Monitor de Mercado y Riesgo")
st.markdown("Plataforma para el análisis en tiempo real de métricas de mercado, riesgo y alertas automatizadas.")

# --- Carga de datos inicial ---
all_coins_df = api_client.get_all_coins_list()
if all_coins_df.empty:
    st.error("No se pudieron cargar los datos iniciales. La aplicación no puede continuar.")
    st.stop()
coin_map = {row['name']: row['id'] for _, row in all_coins_df.iterrows()}

# --- Selección de Activos ---
default_assets = ["Bitcoin", "Ethereum", "Cardano", "Solana", "Dogecoin"]
selected_assets = st.multiselect("Activos a Monitorear:", options=list(coin_map.keys()), default=default_assets)

if not selected_assets:
    st.warning("Seleccione al menos un activo para continuar.")
    st.stop()

# --- Configuración de Alertas en la Barra Lateral ---
st.sidebar.header("Configuración de Alertas de Riesgo")
alerts = {}
with st.sidebar.expander("Alertas de Volatilidad", expanded=True):
    vol_threshold = st.slider("Alerta si la volatilidad anualizada supera (%):", 10, 200, 80)
    alerts['volatility'] = {'threshold': vol_threshold}
with st.sidebar.expander("Alertas de Volumen", expanded=True):
    vol_increase_factor = st.slider("Alerta si el volumen diario supera N veces su media de 20 días:", 1.5, 10.0, 3.0, 0.5)
    alerts['volume'] = {'threshold': vol_increase_factor}

# --- Procesamiento y Visualización de Datos ---
asset_ids = [coin_map[name] for name in selected_assets]
price_data = api_client.get_simple_price(asset_ids)

triggered_alerts = []
all_metrics = []

for asset_name in selected_assets:
    asset_id = coin_map[asset_name]
    hist_data = api_client.get_coin_historical_data(asset_id, days=90)
    
    if not hist_data.empty and price_data and asset_id in price_data:
        volatility = risk_analysis.calculate_volatility(hist_data['price'])
        var_95 = risk_analysis.calculate_var(hist_data['price'])
        is_unusual_volume = risk_analysis.detect_unusual_volume(hist_data['volume'], threshold=alerts['volume']['threshold'])
        
        metrics = {
            'Activo': asset_name,
            'Precio (USD)': price_data[asset_id].get('usd', 0),
            'Cambio (24h)': price_data[asset_id].get('usd_24h_change', 0),
            'Volatilidad Anual (%)': volatility,
            'VaR 95% Diario (%)': var_95,
            'Volumen Inusual': 'Sí' if is_unusual_volume else 'No'
        }
        all_metrics.append(metrics)

        # Chequeo de alertas
        if volatility > alerts['volatility']['threshold']:
            triggered_alerts.append(f"ALERTA DE VOLATILIDAD: **{asset_name}** ha superado el umbral del **{alerts['volatility']['threshold']}%** (Actual: {volatility:.2f}%)")
        if is_unusual_volume:
            triggered_alerts.append(f"ALERTA DE VOLUMEN: **{asset_name}** ha registrado un volumen inusual (superior a {alerts['volume']['threshold']}x la media).")

# --- Dashboard Principal ---
st.header("Alertas de Riesgo Activas")
if triggered_alerts:
    for alert in triggered_alerts:
        st.warning(alert)
else:
    st.success("No hay alertas de riesgo activas según los umbrales configurados.")

st.header("Resumen del Mercado")
if all_metrics:
    metrics_df = pd.DataFrame(all_metrics)
    
    # Métricas agregadas
    avg_volatility = metrics_df['Volatilidad Anual (%)'].mean()
    biggest_gainer = metrics_df.loc[metrics_df['Cambio (24h)'].idxmax()]
    biggest_loser = metrics_df.loc[metrics_df['Cambio (24h)'].idxmin()]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Volatilidad Promedio (Anual)", f"{avg_volatility:.2f}%")
    col2.metric(f"Mayor Subida (24h): {biggest_gainer['Activo']}", f"{biggest_gainer['Cambio (24h)']:.2f}%")
    col3.metric(f"Mayor Caída (24h): {biggest_loser['Activo']}", f"{biggest_loser['Cambio (24h)']:.2f}%")

    # Tabla de datos
    st.dataframe(metrics_df.style.format({
        'Precio (USD)': '${:,.2f}',
        'Cambio (24h)': '{:.2f}%',
        'Volatilidad Anual (%)': '{:.2f}%',
        'VaR 95% Diario (%)': '{:.2f}%'
    }).apply(lambda x: ['background-color: #4CAF50' if v > 0 else 'background-color: #f44336' for v in x], subset=['Cambio (24h)']),
    use_container_width=True)
else:
    st.info("Cargando datos de los activos seleccionados...")