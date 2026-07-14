import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Gestão NanoSignals Pro", layout="wide")

st.title("🚀 Sistema de Gestão Financeira - NanoSignals")

# URL da sua planilha publicada
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRB94ZeKrMAp-UYBpTDrHRVKNfgF_3W9UCwVIQuntrQP7lq2Hd0DHWoWg0Qe8uWjQMoUFMDJ7oQgYrC/pub?output=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(url)
    return df

df = load_data()

# Sidebar para filtros
st.sidebar.header("Filtros de Análise")
responsavel = st.sidebar.multiselect("Filtrar por Responsável:", options=df['Responsavel'].unique())

if responsavel:
    df_filtered = df[df['Responsavel'].isin(responsavel)]
else:
    df_filtered = df

# Métricas Principais
col1, col2, col3 = st.columns(3)
col1.metric("Total de Saídas", f"R$ {df_filtered['Valor'].sum():,.2f}")
col2.metric("Nº de Transações", len(df_filtered))
col3.metric("Média por Transação", f"R$ {df_filtered['Valor'].mean():,.2f}")

# Gráficos
tab1, tab2 = st.tabs(["Visão por Sócio", "Detalhamento"])

with tab1:
    st.subheader("Distribuição de Gastos por Responsável")
    fig = px.pie(df_filtered, values='Valor', names='Responsavel', hole=0.3)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Dados Brutos")
    st.dataframe(df_filtered, use_container_width=True)
