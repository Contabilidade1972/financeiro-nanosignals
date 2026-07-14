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

# --- LAYOUT ---
st.title("🚀 NanoSignals PRO")
aba1, aba2 = st.tabs(["📊 Dashboard", "📝 Lançamentos"])

with aba1:
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM financeiro", conn)
    conn.close()
    
    # Camada de Segurança: Se df estiver vazio ou colunas faltarem, cria um DF seguro
    if df.empty or 'valor' not in df.columns or 'tipo' not in df.columns:
        st.info("Aguardando lançamentos. O sistema está pronto.")
    else:
        # Força conversão e preenche vazios com 0
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
        
        ent = df[df['tipo'] == 'Entrada']['valor'].sum()
        sai = df[df['tipo'] == 'Saída']['valor'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Entradas", f"R$ {ent:,.2f}")
        c2.metric("Saídas", f"R$ {sai:,.2f}")
        c3.metric("Saldo", f"R$ {ent - sai:,.2f}")
        
        st.plotly_chart(px.bar(df, x='responsavel', y='valor', color='tipo'), use_container_width=True)

with aba2:
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM financeiro", conn)
    
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True)
    AgGrid(df, gridOptions=gb.build(), use_container_width=True)
    
    with st.form("lancamento_novo"):
        c1, c2 = st.columns(2)
        data = c1.date_input("Data")
        valor = c2.number_input("Valor", format="%.2f")
        desc = c1.text_input("Descrição")
        resp = c2.text_input("Responsável")
        tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
        if st.form_submit_button("Salvar"):
            c = conn.cursor()
            c.execute("INSERT INTO financeiro (data, valor, descricao, responsavel, tipo) VALUES (?,?,?,?,?)", 
                      (str(data), valor, desc, resp, tipo))
            conn.commit()
            st.rerun()
    conn.close()
