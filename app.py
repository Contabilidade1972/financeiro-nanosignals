import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="NanoSignals PRO", layout="wide")

# Conexão direta e segura
def get_conn():
    return sqlite3.connect('nanosignals_definitivo.db', check_same_thread=False)

# Inicialização mínima
conn = get_conn()
conn.execute('CREATE TABLE IF NOT EXISTS financeiro (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, valor REAL, descricao TEXT, responsavel TEXT, tipo TEXT)')
conn.commit()
conn.close()

st.title("🚀 NanoSignals PRO - Sistema Estável")

aba1, aba2 = st.tabs(["📊 Dashboard", "📝 Lançamentos"])

with aba1:
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM financeiro", conn)
    conn.close()
    
    if df.empty:
        st.warning("O sistema está vazio. Adicione lançamentos na aba 'Lançamentos'.")
    else:
        # Força limpeza básica para evitar erros
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
        
        ent = df[df['tipo'] == 'Entrada']['valor'].sum()
        sai = df[df['tipo'] == 'Saída']['valor'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Entradas", f"R$ {ent:,.2f}")
        c2.metric("Saídas", f"R$ {sai:,.2f}")
        c3.metric("Saldo", f"R$ {ent - sai:,.2f}")
        
        st.write("Registros encontrados:", len(df))
        st.dataframe(df)

with aba2:
    with st.form("lancamento_form"):
        data = st.date_input("Data")
        valor = st.number_input("Valor", format="%.2f")
        desc = st.text_input("Descrição")
        resp = st.text_input("Responsável")
        tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
        
        if st.form_submit_button("Salvar Registro"):
            conn = get_conn()
            conn.execute("INSERT INTO financeiro (data, valor, descricao, responsavel, tipo) VALUES (?,?,?,?,?)", 
                         (str(data), valor, desc, resp, tipo))
            conn.commit()
            conn.close()
            st.success("Salvo com sucesso!")
            st.rerun()
