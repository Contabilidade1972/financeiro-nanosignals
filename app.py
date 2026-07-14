import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# Configuração de Estilo
st.set_page_config(page_title="NanoSignals PRO", layout="wide")
st.markdown("""
    <style>
    .main {background-color: #f5f7f9;}
    .stButton>button {width: 100%; border-radius: 5px; font-weight: bold;}
    </style>
    """, unsafe_allow_html=True)

# Banco de Dados
conn = sqlite3.connect('nanosignals_pro.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS financeiro 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, valor REAL, descricao TEXT, responsavel TEXT, tipo TEXT)''')
conn.commit()

# Sidebar de Navegação
st.sidebar.title("🚀 NanoSignals PRO")
menu = st.sidebar.radio("Navegação", ["Dashboard Executivo", "Gestão de Lançamentos", "Importar Histórico", "Relatórios"])

# Lógica de Importação (Botão para carregar suas planilhas)
if menu == "Importar Histórico":
    st.subheader("📥 Carga de Histórico (Planilhas Antigas)")
    uploaded_files = st.file_uploader("Arraste seus arquivos CSV aqui", accept_multiple_files=True)
    if uploaded_files:
        for file in uploaded_files:
            df = pd.read_csv(file)
            df.to_sql('financeiro', conn, if_exists='append', index=False)
            st.success(f"Arquivo {file.name} importado!")

# Dashboard
if menu == "Dashboard Executivo":
    st.title("📊 Dashboard Executivo")
    df = pd.read_sql_query("SELECT * FROM financeiro", conn)
    if not df.empty:
        c1, c2 = st.columns(2)
        c1.plotly_chart(px.bar(df, x='responsavel', y='valor', color='tipo', title="Performance por Sócio"), use_container_width=True)
        c2.plotly_chart(px.pie(df, values='valor', names='tipo', title="Composição Financeira"), use_container_width=True)
    else:
        st.info("Nenhum dado encontrado. Acesse a aba 'Importar Histórico'.")

# Gestão de Dados
elif menu == "Gestão de Lançamentos":
    st.title("📝 Registro de Operações")
    with st.form("lancamento_form"):
        col1, col2 = st.columns(2)
        data = col1.date_input("Data")
        valor = col1.number_input("Valor", format="%.2f")
        desc = col2.text_input("Descrição")
        resp = col2.text_input("Responsável")
        tipo = st.selectbox("Natureza", ["Entrada", "Saída"])
        if st.form_submit_button("Confirmar Lançamento"):
            c.execute("INSERT INTO financeiro (data, valor, descricao, responsavel, tipo) VALUES (?,?,?,?,?)", 
                      (str(data), valor, desc, resp, tipo))
            conn.commit()
            st.success("Lançamento efetuado com sucesso!")

# Relatórios
elif menu == "Relatórios":
    st.title("📑 Central de Relatórios")
    df = pd.read_sql_query("SELECT * FROM financeiro", conn)
    st.dataframe(df, use_container_width=True)
    st.download_button("Exportar para Excel (.csv)", df.to_csv(index=False), "relatorio.csv")
