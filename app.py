import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="Gestão Financeira NanoSignals", layout="wide")
st.title("🚀 Sistema de Gestão Financeira - NanoSignals")

def conectar_gsheets():
    # Carrega as chaves do Secrets
    creds_dict = {
        "type": st.secrets["type"],
        "project_id": st.secrets["project_id"],
        "private_key_id": st.secrets["private_key_id"],
        "private_key": st.secrets["private_key"],
        "client_email": st.secrets["client_email"],
        "client_id": st.secrets["client_id"],
        "auth_uri": st.secrets["auth_uri"],
        "token_uri": st.secrets["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["client_x509_cert_url"]
    }
    # Escopo para Drive e Planilhas
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

# Conexão com tratamento de erro detalhado
try:
    client = conectar_gsheets()
    # Usando o ID fixo da planilha
    sheet = client.open_by_key("1B_6Gd5l0lv3MeXt4WYBfZ9wa9AGxrf5SIJW54697G6M").sheet1
    df = pd.DataFrame(sheet.get_all_records())
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)
except Exception as e:
    st.error(f"Erro detalhado de conexão: {e}")
    st.info("Verifique se o e-mail do robô nanosignals-bot@precise-ascent-347615.iam.gserviceaccount.com tem acesso de Editor à planilha.")
    st.stop()

# Abas
aba1, aba2, aba3 = st.tabs(["Dashboard", "Relatório", "Novo Lançamento"])

with aba1:
    col1, col2 = st.columns(2)
    col1.plotly_chart(px.bar(df, x='Responsavel', y='Valor', color='Tipo'), use_container_width=True)
    col2.plotly_chart(px.pie(df, values='Valor', names='Responsavel'), use_container_width=True)

with aba2:
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True)
    AgGrid(df, gridOptions=gb.build(), update_mode=GridUpdateMode.VALUE_CHANGED, use_container_width=True)

with aba3:
    with st.form("form_novo"):
        valor = st.number_input("Valor (R$)", min_value=0.0)
        desc = st.text_input("Descrição")
        resp = st.selectbox("Responsável", df['Responsavel'].unique() if not df.empty else ["Manual"])
        tipo = st.radio("Natureza:", ["Entrada", "Saída"])
        if st.form_submit_button("Confirmar"):
            sheet.append_row([valor, "14/07/2026", desc, resp, tipo])
            st.success("Lançamento concluído!")
            st.rerun()
