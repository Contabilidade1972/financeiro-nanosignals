import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="NanoSignals PRO", layout="wide")

# --- BANCO DE DADOS (Persistente) ---
def get_db():
    return sqlite3.connect('nanosignals_pro.db', check_same_thread=False)

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS financeiro 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, valor REAL, descricao TEXT, responsavel TEXT, tipo TEXT)''')
    
    # Verifica se a tabela está vazia. Se estiver, insere dados iniciais (Exemplo de estrutura)
    c.execute("SELECT count(*) FROM financeiro")
    if c.fetchone()[0] == 0:
        # Aqui insiro uma carga inicial limpa baseada no que você me enviou
        # Adicionei os principais itens identificados nas suas planilhas
        registros_iniciais = [
            ('2026-07-01', 300.0, 'Contadora', 'NanoSignals', 'Saída'),
            ('2026-07-13', 157.0, 'Biominas', 'Luis', 'Saída'),
            ('2026-07-01', 81.8, 'Google Workspace', 'Luis', 'Saída'),
            ('2025-04-15', 200.0, 'Curso Precificação', 'NanoSignals', 'Saída'),
            ('2025-07-07', 243.97, 'Aporte Plenum', 'Alice', 'Entrada')
        ]
        c.executemany("INSERT INTO financeiro (data, valor, descricao, responsavel, tipo) VALUES (?,?,?,?,?)", registros_iniciais)
        conn.commit()
    conn.close()

init_db()

# --- INTERFACE ---
st.title("🚀 NanoSignals PRO - Sistema Autônomo")
aba1, aba2 = st.tabs(["📊 Dashboard Executivo", "📝 Gestão de Lançamentos"])

with aba1:
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM financeiro", conn)
    conn.close()
    
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Entradas", f"R$ {df[df['tipo']=='Entrada']['valor'].sum():,.2f}")
        c2.metric("Saídas", f"R$ {df[df['tipo']=='Saída']['valor'].sum():,.2f}")
        c3.metric("Saldo", f"R$ {df[df['tipo']=='Entrada']['valor'].sum() - df[df['tipo']=='Saída']['valor'].sum():,.2f}")
        
        st.plotly_chart(px.bar(df, x='responsavel', y='valor', color='tipo'), use_container_width=True)

with aba2:
    st.header("Lançamentos")
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM financeiro", conn)
    
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True)
    AgGrid(df, gridOptions=gb.build(), use_container_width=True)
    
    with st.form("add_novo"):
        c1, c2 = st.columns(2)
        data = c1.date_input("Data")
        valor = c2.number_input("Valor", format="%.2f")
        desc = c1.text_input("Descrição")
        resp = c2.text_input("Responsável")
        tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
        if st.form_submit_button("Salvar Registro"):
            c = conn.cursor()
            c.execute("INSERT INTO financeiro (data, valor, descricao, responsavel, tipo) VALUES (?,?,?,?,?)", 
                      (str(data), valor, desc, resp, tipo))
            conn.commit()
            st.rerun()
    conn.close()
