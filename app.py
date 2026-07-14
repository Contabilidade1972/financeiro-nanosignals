import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Configuração Profissional
st.set_page_config(page_title="NanoSignals PRO", layout="wide", initial_sidebar_state="expanded")

# Banco de Dados
conn = sqlite3.connect('nanosignals_pro.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS financeiro 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, valor REAL, descricao TEXT, responsavel TEXT, tipo TEXT)''')
conn.commit()

# Sidebar de Navegação
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/combo-chart.png", width=60)
    st.title("NanoSignals PRO")
    menu = st.radio("MENU", ["Dashboard Executivo", "Lançamentos e Edição", "Importar Dados"])
    st.info("Sistema de Gestão Financeira Autônoma")

# Lógica de Importação
if menu == "Importar Dados":
    st.title("📥 Importação de Histórico")
    uploaded_files = st.file_uploader("Suba seus arquivos CSV", accept_multiple_files=True)
    if uploaded_files:
        for file in uploaded_files:
            df = pd.read_csv(file)
            # Normalização forçada para garantir que os dados entrem no banco
            df.columns = ['data', 'valor', 'descricao', 'responsavel', 'tipo']
            df.to_sql('financeiro', conn, if_exists='append', index=False)
            st.success(f"Arquivo {file.name} processado com sucesso!")

# Dashboard
if menu == "Dashboard Executivo":
    st.title("📊 Dashboard")
    df = pd.read_sql_query("SELECT * FROM financeiro", conn)
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Receita Total", f"R$ {df[df['tipo']=='Entrada']['valor'].sum():,.2f}")
        col2.metric("Despesas Total", f"R$ {df[df['tipo']=='Saída']['valor'].sum():,.2f}")
        col3.metric("Saldo", f"R$ {df[df['tipo']=='Entrada']['valor'].sum() - df[df['tipo']=='Saída']['valor'].sum():,.2f}")
        
        c1, c2 = st.columns(2)
        c1.plotly_chart(px.bar(df, x='responsavel', y='valor', color='tipo', title="Gastos por Sócio"), use_container_width=True)
        c2.plotly_chart(px.pie(df, values='valor', names='tipo', title="Composição Financeira"), use_container_width=True)
    else:
        st.warning("Sem dados. Use a aba 'Importar Dados'.")

# Gestão de Dados (Tabela Editável)
elif menu == "Lançamentos e Edição":
    st.title("📝 Lançamentos")
    df = pd.read_sql_query("SELECT * FROM financeiro", conn)
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True, filter=True)
    gb.configure_selection('single')
    AgGrid(df, gridOptions=gb.build(), update_mode=GridUpdateMode.VALUE_CHANGED, height=400, use_container_width=True)
    
    st.divider()
    with st.form("add_form"):
        c1, c2, c3 = st.columns(3)
        data = c1.date_input("Data")
        valor = c2.number_input("Valor", format="%.2f")
        desc = c3.text_input("Descrição")
        resp = c1.text_input("Responsável")
        tipo = c2.selectbox("Tipo", ["Entrada", "Saída"])
        if st.form_submit_button("Confirmar Lançamento"):
            c.execute("INSERT INTO financeiro (data, valor, descricao, responsavel, tipo) VALUES (?,?,?,?,?)", 
                      (str(data), valor, desc, resp, tipo))
            conn.commit()
            st.rerun()
