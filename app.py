import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Configuração da página
st.set_page_config(page_title="NanoSignals PRO", layout="wide", initial_sidebar_state="expanded")

# --- BANCO DE DADOS ---
def get_db_connection():
    conn = sqlite3.connect('nanosignals_pro.db', check_same_thread=False)
    return conn

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

# --- SIDEBAR ---
with st.sidebar:
    st.title("🚀 NanoSignals PRO")
    menu = st.radio("MENU", ["Dashboard Executivo", "Lançamentos e Edição", "Importar Dados"])

# --- LÓGICA DE IMPORTAÇÃO (MAIS ROBUSTA) ---
if menu == "Importar Dados":
    st.title("📥 Importação de Histórico")
    uploaded_files = st.file_uploader("Suba seus arquivos CSV aqui", accept_multiple_files=True)
    if uploaded_files:
        conn = get_db_connection()
        for file in uploaded_files:
            try:
                # O parâmetro 'on_bad_lines="skip"' ignora linhas que estão fora do padrão
                # O parâmetro 'sep' tenta detectar automaticamente ou assume vírgula
                df = pd.read_csv(file, encoding='latin-1', on_bad_lines='skip', sep=None, engine='python')
                
                # Seleciona apenas as 5 colunas que importam, independentemente do nome original
                df = df.iloc[:, :5]
                df.columns = ['data', 'valor', 'descricao', 'responsavel', 'tipo']
                
                # Remove linhas onde todos os campos são nulos
                df = df.dropna(how='all')
                
                # Garante que dados vazios não quebrem o banco
                df.to_sql('financeiro', conn, if_exists='append', index=False)
                st.success(f"Arquivo {file.name} processado com sucesso!")
            except Exception as e:
                st.error(f"Erro no arquivo {file.name}: {e}")
        conn.close()

# --- DASHBOARD EXECUTIVO ---
elif menu == "Dashboard Executivo":
    st.title("📊 Dashboard Executivo")
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM financeiro", conn)
    conn.close()
    
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Receita Total", f"R$ {df[df['tipo']=='Entrada']['valor'].sum():,.2f}")
        c2.metric("Despesa Total", f"R$ {df[df['tipo']=='Saída']['valor'].sum():,.2f}")
        c3.metric("Saldo Líquido", f"R$ {df[df['tipo']=='Entrada']['valor'].sum() - df[df['tipo']=='Saída']['valor'].sum():,.2f}")
        
        st.write("---")
        c1, c2 = st.columns(2)
        c1.plotly_chart(px.bar(df, x='responsavel', y='valor', color='tipo', title="Gastos por Sócio"), use_container_width=True)
        c2.plotly_chart(px.pie(df, values='valor', names='tipo', title="Composição Financeira"), use_container_width=True)
    else:
        st.info("Nenhum dado encontrado. Acesse a aba 'Importar Dados'.")

# --- LANÇAMENTOS E EDIÇÃO ---
elif menu == "Lançamentos e Edição":
    st.title("📝 Lançamentos")
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM financeiro", conn)
    
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True, filter=True)
    AgGrid(df, gridOptions=gb.build(), update_mode=GridUpdateMode.VALUE_CHANGED, height=400, use_container_width=True)
    
    with st.form("add_form"):
        st.subheader("Novo Lançamento Manual")
        c1, c2, c3 = st.columns(3)
        data = c1.date_input("Data")
        valor = c2.number_input("Valor", min_value=0.0, format="%.2f")
        desc = c3.text_input("Descrição")
        resp = c1.text_input("Responsável")
        tipo = c2.selectbox("Natureza", ["Entrada", "Saída"])
        if st.form_submit_button("Confirmar Lançamento"):
            c = conn.cursor()
            c.execute("INSERT INTO financeiro (data, valor, descricao, responsavel, tipo) VALUES (?,?,?,?,?)", 
                      (str(data), valor, desc, resp, tipo))
            conn.commit()
            st.rerun()
    conn.close()
