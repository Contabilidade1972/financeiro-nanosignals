import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="Gestão Financeira NanoSignals", layout="wide")

st.title("🚀 Sistema de Gestão Financeira - NanoSignals")

# Conectando ao Google Sheets usando as variáveis do Secrets
def conectar_gsheets():
    creds_dict = {
        "type": st.secrets["type"],
        "project_id": st.secrets["project_id"],
        "private_key_id": st.secrets["private_key_id"],
        "private_key": st.secrets["private_key"].replace('\\n', '\n'),
        "client_email": st.secrets["client_email"],
        "client_id": st.secrets["client_id"],
        "auth_uri": st.secrets["auth_uri"],
        "token_uri": st.secrets["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["client_x509_cert_url"]
    }
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client

try:
    client = conectar_gsheets()
    sheet = client.open("Base_Financeira_Oficial").sheet1
    df = pd.DataFrame(sheet.get_all_records())
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)
except Exception as e:
    st.error(f"Erro ao conectar: {e}")
    st.stop()

# Abas
aba1, aba2, aba3 = st.tabs(["Dashboard", "Relatório", "Novo Lançamento"])

with aba1:
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.bar(df, x='Responsavel', y='Valor', color='Tipo'), use_container_width=True)
    with col2:
        st.plotly_chart(px.pie(df, values='Valor', names='Responsavel'), use_container_width=True)

with aba2:
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True)
    AgGrid(df, gridOptions=gb.build(), update_mode=GridUpdateMode.VALUE_CHANGED)

with aba3:
    with st.form("form_novo"):
        valor = st.number_input("Valor")
        desc = st.text_input("Descrição")
        resp = st.selectbox("Responsável", df['Responsavel'].unique())
        tipo = st.radio("Tipo", ["Entrada", "Saída"])
        if st.form_submit_button("Registrar"):
            sheet.append_row([valor, "2026-07-14", desc, resp, tipo])
            st.success("Registrado!")
