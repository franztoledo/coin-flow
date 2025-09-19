import streamlit as st

def initialize_session_state():
    """Inicializa el estado de la sesión para las alertas si no existe."""
    if 'alerts' not in st.session_state:
        st.session_state.alerts = []

def add_alert(coin_id, coin_name, target_price):
    """Añade una nueva alerta a la lista en el estado de sesión."""
    if not any(alert['id'] == coin_id for alert in st.session_state.alerts):
        st.session_state.alerts.append({'id': coin_id, 'name': coin_name, 'target': target_price})
        return True
    return False

def remove_alerts(alerts_to_remove):
    """Elimina una o más alertas de la lista."""
    st.session_state.alerts = [alert for alert in st.session_state.alerts if alert not in alerts_to_remove]