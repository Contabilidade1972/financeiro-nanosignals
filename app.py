import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="NanoSignals PRO", layout="wide")

def get_db():
    return sqlite3.connect('nanosignals_pro.db', check_same_thread=False)

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS financeiro 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, valor REAL, descricao TEXT, responsavel TEXT, tipo TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- NAVEGAÇÃO ---
st.sidebar.title("🚀 NanoSignals PRO")
menu = st.sidebar.radio("MENU", ["Dashboard Executivo", "Lançamentos e Edição", "Importar Dados"])

# --- LÓGICA DE IMPORTAÇÃO ---
if menu == "Importar Dados":
    st.title("📥 Importação de Histórico")
    files = st.file_uploader("Suba seus CSVs", accept_multiple_files=True)
    if files:
        conn = get_db()
        for file in files:
            try:
                df = pd.read_csv(file, encoding='latin-1', on_bad_lines='skip', sep=None, engine='python')
                df = df.iloc[:, :5]
                df.columns = ['data', 'valor', 'descricao', 'responsavel', 'tipo']
                # Força conversão de valor antes de salvar
                df['valor'] = df['valor'].replace(r'[R$\s]', '', regex=True).replace(',', '.', regex=True)
                df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
                df.to_sql('financeiro', conn, if_exists='append', index=False)
                st.success(f"Arquivo {file.name} carregado!")
            except Exception as e:
                st.error(f"Erro: {e}")
        conn.close()

# --- DASHBOARD EXECUTIVO ---
elif menu == "Dashboard Executivo":
    st.title("📊 Dashboard Executivo")
    conn = get_db()
    # Leitura com conversão forçada
    df = pd.read_sql_query("SELECT * FROM financeiro", conn)
    conn.close()
    
    if not df.empty:
        # Conversão absoluta para não dar erro no gráfico
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Entradas", f"R$ {df[df['tipo']=='Entrada']['valor'].sum():,.2f}")
        c2.metric("Saídas", f"R$ {df[df['tipo']=='Saída']['valor'].sum():,.2f}")
        c3.metric("Saldo", f"R$ {df[df['tipo']=='Entrada']['valor'].sum() - df[df['tipo']=='Saída']['valor'].sum():,.2f}")
        
        st.plotly_chart(px.bar(df, x='responsavel', y='valor', color='tipo'), use_container_width=True)
    else:
        st.info("A base está vazia. Vá em 'Importar Dados'.")

# --- LANÇAMENTOS ---
elif menu == "Lançamentos e Edição":
    st.title("📝 Lançamentos")
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM financeiro", conn)
    AgGrid(df, use_container_width=True)
    conn.close()
