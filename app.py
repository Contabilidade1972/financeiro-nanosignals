import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="NanoSignals PRO", layout="wide")

# --- BANCO DE DADOS (O Coração do Sistema) ---
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

# --- NAVEGAÇÃO E LAYOUT ---
st.title("🚀 NanoSignals PRO - Sistema Integrado")
aba1, aba2, aba3 = st.tabs(["📊 Dashboard Executivo", "📝 Gestão e Lançamentos", "📥 Importar Histórico"])

# ABA 1: Dashboard
with aba1:
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM financeiro", conn)
    conn.close()
    
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Entradas", f"R$ {df[df['tipo']=='Entrada']['valor'].sum():,.2f}")
        c2.metric("Saídas", f"R$ {df[df['tipo']=='Saída']['valor'].sum():,.2f}")
        c3.metric("Saldo", f"R$ {df[df['tipo']=='Entrada']['valor'].sum() - df[df['tipo']=='Saída']['valor'].sum():,.2f}")
        st.plotly_chart(px.bar(df, x='responsavel', y='valor', color='tipo', title="Performance por Sócio"), use_container_width=True)
    else:
        st.info("O sistema está vazio. Use a aba 'Importar Histórico' para carregar seus arquivos.")

# ABA 2: Lançamentos
with aba2:
    st.header("Lançamentos Detalhados")
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM financeiro", conn)
    
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True, filter=True)
    AgGrid(df, gridOptions=gb.build(), height=300, use_container_width=True)
    
    with st.form("add_form"):
        c1, c2, c3 = st.columns(3)
        data = c1.date_input("Data")
        valor = c2.number_input("Valor", format="%.2f")
        desc = c3.text_input("Descrição")
        resp = c1.text_input("Responsável")
        tipo = c2.selectbox("Natureza", ["Entrada", "Saída"])
        if st.form_submit_button("Salvar Registro"):
            c = conn.cursor()
            c.execute("INSERT INTO financeiro (data, valor, descricao, responsavel, tipo) VALUES (?,?,?,?,?)", (str(data), valor, desc, resp, tipo))
            conn.commit()
            st.rerun()
    conn.close()

# ABA 3: Importação
with aba3:
    st.header("Importação de Planilhas Antigas")
    uploaded_files = st.file_uploader("Suba seus CSVs", accept_multiple_files=True)
    if uploaded_files:
        conn = get_db()
        for file in uploaded_files:
            try:
                df = pd.read_csv(file, encoding='latin-1', on_bad_lines='skip', sep=None, engine='python')
                df = df.iloc[:, :5]
                df.columns = ['data', 'valor', 'descricao', 'responsavel', 'tipo']
                df.to_sql('financeiro', conn, if_exists='append', index=False)
                st.success(f"Arquivo {file.name} carregado!")
            except Exception as e:
                st.error(f"Erro no arquivo {file.name}: {e}")
        conn.close()
