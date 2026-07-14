import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="NanoSignals PRO", layout="wide")

# --- BANCO DE DADOS ---
def get_db():
    conn = sqlite3.connect('nanosignals_pro.db', check_same_thread=False)
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS financeiro 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, valor REAL, descricao TEXT, responsavel TEXT, tipo TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- NAVEGAÇÃO ---
st.title("🚀 NanoSignals PRO")
aba1, aba2, aba3 = st.tabs(["📊 Dashboard Executivo", "📝 Gestão e Lançamentos", "📥 Importar Histórico"])

# ABA 1: Dashboard
with aba1:
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM financeiro", conn)
    conn.close()
    
    if not df.empty:
        # Conversão forçada: garante que 'valor' seja número e 'tipo' seja texto
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
        df['tipo'] = df['tipo'].astype(str)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Entradas", f"R$ {df[df['tipo']=='Entrada']['valor'].sum():,.2f}")
        c2.metric("Saídas", f"R$ {df[df['tipo']=='Saída']['valor'].sum():,.2f}")
        c3.metric("Saldo", f"R$ {df[df['tipo']=='Entrada']['valor'].sum() - df[df['tipo']=='Saída']['valor'].sum():,.2f}")
        
        st.write("---")
        c1, c2 = st.columns(2)
        c1.plotly_chart(px.bar(df, x='responsavel', y='valor', color='tipo'), use_container_width=True)
        c2.plotly_chart(px.pie(df, values='valor', names='tipo'), use_container_width=True)
    else:
        st.info("O sistema está vazio. Importe seus arquivos CSV.")

# ABA 2: Gestão
with aba2:
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM financeiro", conn)
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True)
    AgGrid(df, gridOptions=gb.build(), update_mode=GridUpdateMode.VALUE_CHANGED, use_container_width=True)
    conn.close()

# ABA 3: Importação
with aba3:
    uploaded_files = st.file_uploader("Suba seus CSVs", accept_multiple_files=True)
    if uploaded_files:
        conn = get_db()
        for file in uploaded_files:
            try:
                df = pd.read_csv(file, encoding='latin-1', on_bad_lines='skip', sep=None, engine='python')
                df = df.iloc[:, :5]
                df.columns = ['data', 'valor', 'descricao', 'responsavel', 'tipo']
                
                # LIMPEZA CRÍTICA: Remove símbolos de moeda e converte para número na hora da carga
                df['valor'] = df['valor'].replace(r'[R$\s]', '', regex=True).replace(',', '.', regex=True)
                df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
                
                df.to_sql('financeiro', conn, if_exists='append', index=False)
                st.success(f"Sucesso: {file.name}")
            except Exception as e:
                st.error(f"Erro no arquivo {file.name}: {e}")
        conn.close()
