import streamlit as st

from modules.dashboard_view import render_dashboard
from modules.history_view import render_historico
from modules.upload_view import render_upload


st.set_page_config(page_title="Orçamento Familiar", layout="wide")
st.title("📊 Orçamento Familiar 2.0")

aba_dashboard, aba_historico, aba_upload = st.tabs(
    ["Dashboard", "Histórico", "Atualização de Dados"]
)

with aba_dashboard:
    render_dashboard()

with aba_historico:
    render_historico()

with aba_upload:
    render_upload()
