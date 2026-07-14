import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Configuração da Página
st.set_page_config(page_title="NanoSignals PRO", layout="wide")

# Conexão com o Banco de Dados
def get_db():
    return sqlite3.connect('nanosignals_final.db', check_same_thread=False)

# Inicialização
conn = get_db()
conn.execute('CREATE TABLE IF NOT EXISTS financeiro (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, valor REAL, descricao TEXT, responsavel TEXT, tipo TEXT)')
conn.commit()
conn.close()

st.title("🚀 NanoSignals PRO - Sistema Estável")

aba1, aba2 = st.tabs(["📊 Dashboard Executivo", "📝 Gestão de Lançamentos"])

with aba1:
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM financeiro", conn)
    conn.close()
    
    if df.empty:
        st.warning("O sistema está vazio. Adicione registros na aba 'Gestão de Lançamentos'.")
    else:
        # Limpeza robusta para exibição
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
        
        ent = df[df['tipo'] == 'Entrada']['valor'].sum()
        sai = df[df['tipo'] == 'Saída']['valor'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Entradas", f"R$ {ent:,.2f}")
        c2.metric("Saídas", f"R$ {sai:,.2f}")
        c3.metric("Saldo", f"R$ {ent - sai:,.2f}")
        
        st.plotly_chart(px.bar(df, x='responsavel', y='valor', color='tipo'), use_container_width=True)

with aba2:
    st.subheader("Registrar Lançamento")
    with st.form("lancamento_form"):
        col1, col2 = st.columns(2)
        data = col1.date_input("Data")
        valor = col1.number_input("Valor", format="%.2f")
        desc = col2.text_input("Descrição")
        resp = col2.text_input("Responsável")
        tipo = st.selectbox("Natureza", ["Entrada", "Saída"])
        
        if st.form_submit_button("Salvar no Banco"):
            conn = get_db()
            conn.execute("INSERT INTO financeiro (data, valor, descricao, responsavel, tipo) VALUES (?,?,?,?,?)", 
                         (str(data), valor, desc, resp, tipo))
            conn.commit()
            conn.close()
            st.success("Salvo com sucesso!")
            st.rerun()

    st.subheader("Registros Atuais")
    conn = get_db()
    df_lista = pd.read_sql_query("SELECT * FROM financeiro", conn)
    st.dataframe(df_lista, use_container_width=True)
    conn.close()
