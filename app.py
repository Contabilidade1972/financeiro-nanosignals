import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard NanoSignals", layout="wide")
st.title("📊 Dashboard Financeiro - NanoSignals")

# Link da sua planilha (Google Sheets publicada como CSV)
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRB94ZeKrMAp-UYBpTDrHRVKNfgF_3W9UCwVIQuntrQP7lq2Hd0DHWoWg0Qe8uWjQMoUFMDJ7oQgYrC/pub?output=csv"

@st.cache_data
def load_data():
    return pd.read_csv(url)

df = load_data()

# Exibição de métricas
total_saidas = df[df['Tipo'] == 'Saída']['Valor'].sum()
st.metric("Total de Saídas", f"R$ {total_saidas:,.2f}")

# Gráfico
st.subheader("Análise por Sócio")
chart_data = df.groupby('Responsavel')['Valor'].sum()
st.bar_chart(chart_data)

st.dataframe(df)
