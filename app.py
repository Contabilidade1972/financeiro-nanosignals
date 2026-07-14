import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Configuração da Página
st.set_page_config(page_title="NanoSignals PRO", layout="wide")

# Função de Conexão com tratamento de erro
def get_db_connection():
    conn = sqlite3.connect('nanosignals_pro.db', check_same_thread=False)
    return conn

# Inicialização do Banco e Tabela (Sempre executado na carga)
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS financeiro 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  data TEXT, 
                  valor REAL, 
                  descricao TEXT, 
                  responsavel TEXT, 
                  tipo TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Sidebar
menu = st.sidebar.radio("Navegação", ["Dashboard", "Lançamentos", "Importar Planilhas"])

# Lógica das abas
if menu == "Importar Planilhas":
    st.title("📥 Importar Dados")
    uploaded_files = st.file_uploader("Suba seus CSVs aqui", accept_multiple_files=True)
    if uploaded_files:
        conn = get_db_connection()
        for file in uploaded_files:
            try:
                df = pd.read_csv(file)
                df.columns = ['data', 'valor', 'descricao', 'responsavel', 'tipo']
                df.to_sql('financeiro', conn, if_exists='append', index=False)
                st.success(f"Sucesso: {file.name}")
            except Exception as e:
                st.error(f"Erro no arquivo {file.name}: {e}")
        conn.close()

elif menu == "Dashboard":
    st.title("📊 Dashboard Executivo")
    conn = get_db_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM financeiro", conn)
        if not df.empty:
            # Métricas
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Entradas", f"R$ {df[df['tipo']=='Entrada']['valor'].sum():,.2f}")
            c2.metric("Total Saídas", f"R$ {df[df['tipo']=='Saída']['valor'].sum():,.2f}")
            
            # Gráficos
            c1, c2 = st.columns(2)
            c1.plotly_chart(px.bar(df, x='responsavel', y='valor', color='tipo'), use_container_width=True)
            c2.plotly_chart(px.pie(df, values='valor', names='tipo'), use_container_width=True)
        else:
            st.warning("Banco vazio. Vá para 'Importar Planilhas' e envie seus arquivos.")
    except Exception:
        st.error("A tabela ainda está sendo criada. Tente atualizar a página (F5).")
    conn.close()

elif menu == "Lançamentos":
    st.title("📝 Lançamentos")
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM financeiro", conn)
    AgGrid(df, use_container_width=True)
    conn.close()
