import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da Página
st.set_page_config(page_title="Gestão Financeira NanoSignals", layout="wide")

st.title("🚀 Sistema de Gestão Financeira - NanoSignals")

# URL da planilha publicada
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRB94ZeKrMAp-UYBpTDrHRVKNfgF_3W9UCwVIQuntrQP7lq2Hd0DHWoWg0Qe8uWjQMoUFMDJ7oQgYrC/pub?output=csv"

# Função para carregar e limpar dados
@st.cache_data
def load_data():
    df = pd.read_csv(url)
    # Limpeza básica: remove linhas vazias e trata valores nulos
    df = df.dropna(subset=['Valor'])
    df['Responsavel'] = df['Responsavel'].fillna('Não Definido')
    df['Descricao'] = df['Descricao'].fillna('Sem Descrição')
    return df

# Carregar dados
try:
    df = load_data()

    # Layout em Abas
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Relatório Detalhado", "Novo Lançamento"])

    with tab1:
        st.subheader("Visão Geral")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Saídas", f"R$ {df[df['Tipo'] == 'Saída']['Valor'].sum():,.2f}")
        col2.metric("Total de Entradas", f"R$ {df[df['Tipo'] == 'Entrada']['Valor'].sum():,.2f}")
        col3.metric("Saldo Atual", f"R$ {(df[df['Tipo'] == 'Entrada']['Valor'].sum() - df[df['Tipo'] == 'Saída']['Valor'].sum()):,.2f}")
        
        st.subheader("Distribuição de Gastos")
        fig = px.pie(df[df['Tipo'] == 'Saída'], values='Valor', names='Responsavel', hole=0.4, title="Gastos por Sócio")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Detalhamento de Transações")
        st.dataframe(df, use_container_width=True)

    with tab3:
        st.subheader("Lançamento Manual")
        st.info("Para salvar novos dados diretamente, configuraremos o acesso via API na próxima etapa.")
        with st.form("form_novo_lancamento"):
            data_lanc = st.date_input("Data")
            valor_lanc = st.number_input("Valor", min_value=0.0)
            desc_lanc = st.text_input("Descrição")
            resp_lanc = st.selectbox("Responsável", ["Alice", "Fernanda", "Flávio", "Luis", "Nextrial"])
            tipo_lanc = st.radio("Tipo", ["Entrada", "Saída"])
            
            if st.form_submit_button("Registrar"):
                st.warning("Funcionalidade de escrita em desenvolvimento (requer credenciais API).")

except Exception as e:
    st.error(f"Erro ao carregar o sistema: {e}")
