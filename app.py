import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="NanoSignals PRO", layout="wide")

# Estilo para forçar um layout organizado
st.markdown("""
    <style>
    .reportview-container .main .block-container {max-width: 1200px; padding-top: 2rem;}
    .css-1544g2n {padding: 1rem 1rem 1rem 1rem;}
    </style>
""", unsafe_allow_html=True)

st.title("🚀 NanoSignals PRO - Sistema de Gestão")

# Conexão (Centralizada)
conn = sqlite3.connect('nanosignals_v3.db', check_same_thread=False)

# Menu superior (Mais limpo que sidebar)
aba1, aba2 = st.tabs(["📊 Visão Executiva", "⚙️ Gestão de Dados"])

with aba1:
    st.header("Indicadores Gerais")
    # Colunas fixas
    col1, col2, col3 = st.columns(3)
    col1.metric("Saldo Total", "R$ 0,00")
    col2.metric("Entradas", "R$ 0,00")
    col3.metric("Saídas", "R$ 0,00")
    st.info("Aguardando carregamento da base de dados...")

with aba2:
    st.header("Entrada de Dados")
    st.write("Para ter um sistema profissional, a entrada deve ser estruturada.")
    # Formulário em grade
    with st.form("input_fixed"):
        c1, c2 = st.columns(2)
        c1.date_input("Data")
        c2.number_input("Valor")
        c1.text_input("Descrição")
        c2.selectbox("Responsável", ["Luis", "Outros"])
        st.form_submit_button("Salvar Registro")

st.sidebar.markdown("---")
st.sidebar.write("Status: Sistema Pronto.")
