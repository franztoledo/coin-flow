# pages/03_Analisis_de_Correlacion.py
import streamlit as st
import plotly.graph_objects as go
import api_client
import risk_analysis

st.set_page_config(page_title="Análisis de Correlación", page_icon="🔗", layout="wide")

st.title("Análisis de Correlación entre Activos")
st.markdown("Evalúe cómo se mueven dos activos entre sí para optimizar la diversificación de su portafolio.")

# --- Carga de datos y selección ---
all_coins_df = api_client.get_all_coins_list()
if all_coins_df.empty:
    st.error("No se pudieron cargar los datos de activos.")
    st.stop()
coin_map = {row['name']: row['id'] for _, row in all_coins_df.iterrows()}
coin_names = list(coin_map.keys())

col1, col2 = st.columns(2)
asset_a_name = col1.selectbox("Activo A:", options=coin_names, index=coin_names.index("Bitcoin"))
asset_b_name = col2.selectbox("Activo B:", options=coin_names, index=coin_names.index("Ethereum"))

if asset_a_name and asset_b_name and asset_a_name != asset_b_name:
    hist_a = api_client.get_coin_historical_data(coin_map[asset_a_name], days=180)
    hist_b = api_client.get_coin_historical_data(coin_map[asset_b_name], days=180)

    if not hist_a.empty and not hist_b.empty:
        correlation = risk_analysis.calculate_correlation(hist_a['price'], hist_b['price'])
        st.metric(f"Coeficiente de Correlación (180 días)", f"{correlation:.3f}")
        
        # Gráfico
        normalized_a = (hist_a['price'] / hist_a['price'].iloc[0]) * 100
        normalized_b = (hist_b['price'] / hist_b['price'].iloc[0]) * 100
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=normalized_a.index, y=normalized_a, name=asset_a_name))
        fig.add_trace(go.Scatter(x=normalized_b.index, y=normalized_b, name=asset_b_name))
        st.plotly_chart(fig, use_container_width=True)
elif asset_a_name == asset_b_name:
    st.warning("Seleccione dos activos diferentes.")