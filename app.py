import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Configuração da página
st.set_page_config(page_title="Gestão Financeira NanoSignals", layout="wide")
st.title("🚀 Sistema de Gestão Financeira - NanoSignals")

# Função de Conexão com Google Sheets usando Secrets
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

# Carregar dados
try:
    client = conectar_gsheets()
    sheet = client.open("Base_Financeira_Oficial").sheet1
    dados = sheet.get_all_records()
    df = pd.DataFrame(dados)
    
    # Tratamento de dados básico
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)
    df['Responsavel'] = df['Responsavel'].fillna('Não Definido')
except Exception as e:
    st.error(f"Erro ao conectar com a planilha: {e}")
    st.stop()

# Filtros Globais
st.sidebar.header("Filtros")
tipos = st.sidebar.multiselect("Tipo:", options=df['Tipo'].unique())
responsaveis = st.sidebar.multiselect("Sócio:", options=df['Responsavel'].unique())

if tipos: df = df[df['Tipo'].isin(tipos)]
if responsaveis: df = df[df['Responsavel'].isin(responsaveis)]

# Abas do Sistema
aba1, aba2, aba3 = st.tabs(["Dashboard Interativo", "Relatório Detalhado", "Novo Lançamento"])

with aba1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Evolução por Sócio")
        fig_bar = px.bar(df, x='Responsavel', y='Valor', color='Tipo', barmode='group')
        st.plotly_chart(fig_bar, use_container_width=True)
    with col2:
        st.subheader("Distribuição de Valores")
        fig_pie = px.pie(df, values='Valor', names='Responsavel', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

with aba2:
    st.subheader("Relatório Editável")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True, filter=True)
    gb.configure_column("Valor", type=["numericColumn"], valueFormatter="value.toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'})")
    grid_options = gb.build()
    AgGrid(df, gridOptions=grid_options, update_mode=GridUpdateMode.VALUE_CHANGED, theme='streamlit', use_container_width=True)

with aba3:
    st.subheader("Novo Lançamento")
    with st.form("form_registro"):
        data = st.date_input("Data")
        valor = st.number_input("Valor (R$)", min_value=0.0)
        desc = st.text_input("Descrição")
        resp = st.selectbox("Responsável", options=df['Responsavel'].unique().tolist() + ["Outro"])
        tipo = st.radio("Natureza:", ["Entrada", "Saída"])
        if st.form_submit_button("Registrar no Sistema"):
            sheet.append_row([valor, str(data), desc, resp, tipo])
            st.success("Dados enviados com sucesso!")
            st.rerun()
