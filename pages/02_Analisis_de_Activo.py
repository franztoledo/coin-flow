# pages/02_Analisis_de_Activo.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import api_client
import risk_analysis

st.set_page_config(page_title="Análisis de Activo", page_icon="🔎", layout="wide")

st.title("Análisis Profundo por Activo")

# --- Carga de datos y selección ---
all_coins_df = api_client.get_all_coins_list()
if all_coins_df.empty:
    st.error("No se pudieron cargar los datos de activos.")
    st.stop()
coin_map = {row['name']: row['id'] for _, row in all_coins_df.iterrows()}

selected_asset = st.selectbox("Seleccione un Activo para Analizar:", options=list(coin_map.keys()))

if selected_asset:
    asset_id = coin_map[selected_asset]
    hist_data = api_client.get_coin_historical_data(asset_id, days=365)
    
    if not hist_data.empty:
        # --- Métricas de Riesgo del Activo ---
        st.header(f"Métricas de Riesgo para {selected_asset}")
        volatility = risk_analysis.calculate_volatility(hist_data['price'])
        var_95 = risk_analysis.calculate_var(hist_data['price'])
        
        col1, col2 = st.columns(2)
        col1.metric("Volatilidad Anualizada", f"{volatility:.2f}%")
        col2.metric("Valor en Riesgo (VaR 95%) Diario", f"{var_95:.2f}%")

        # --- Gráfico de Precio y Volumen ---
        st.header("Historial de Precio y Volumen")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['price'], name='Precio (USD)', yaxis='y1'))
        fig.add_trace(go.Bar(x=hist_data.index, y=hist_data['volume'], name='Volumen', yaxis='y2', marker_color='rgba(0,100,200,0.3)'))
        fig.update_layout(
            yaxis=dict(title='Precio (USD)'),
            yaxis2=dict(title='Volumen', overlaying='y', side='right', showgrid=False),
            title_text=f"Historial de {selected_asset}"
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- Proyección de Precios ---
        st.header("Proyección de Tendencia de Precios")
        days_to_predict = st.slider("Días a proyectar:", 7, 90, 30)
        
        projection_df = risk_analysis.create_projection(hist_data['price'], days_to_predict)
        
        fig_proj = go.Figure()
        fig_proj.add_trace(go.Scatter(x=hist_data.index, y=hist_data['price'], name='Precio Histórico'))
        fig_proj.add_trace(go.Scatter(x=projection_df['date'], y=projection_df['predicted_price'], name='Proyección de Tendencia', line=dict(dash='dash')))
        fig_proj.update_layout(title=f"Proyección de Tendencia para {selected_asset}")
        st.plotly_chart(fig_proj, use_container_width=True)
        st.info("AVISO: La proyección se basa en una regresión lineal simple de los datos históricos y no constituye asesoramiento financiero. Representa una continuación de la tendencia pasada.")

    else:
        st.error(f"No se pudieron obtener datos históricos para {selected_asset}.")