import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Configuração Global
st.set_page_config(page_title="NanoSignals ERP", layout="wide")

# Inicialização do Banco de Dados Interno
def init_db():
    conn = sqlite3.connect('nanosignals_erp.db', check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS financeiro (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    data DATE, 
                    descricao TEXT, 
                    valor REAL, 
                    tipo TEXT, 
                    status TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Navegação e Estilo
st.title("🚀 NanoSignals ERP")
menu = st.radio("Módulo:", ["Dashboard", "Contas a Pagar/Receber", "Cadastros"], horizontal=True)

# --- MÓDULO DASHBOARD ---
if menu == "Dashboard":
    st.header("📊 Visão Geral")
    conn = sqlite3.connect('nanosignals_erp.db')
    df = pd.read_sql_query("SELECT * FROM financeiro", conn)
    conn.close()
    
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        total_rec = df[df['tipo']=='Receber']['valor'].sum()
        total_pag = df[df['tipo']=='Pagar']['valor'].sum()
        col1.metric("Total a Receber", f"R$ {total_rec:,.2f}")
        col2.metric("Total a Pagar", f"R$ {total_pag:,.2f}")
        col3.metric("Saldo Líquido", f"R$ {total_rec - total_pag:,.2f}")
        st.plotly_chart(px.bar(df, x='data', y='valor', color='tipo', barmode='group'), use_container_width=True)
    else:
        st.info("Nenhum movimento registrado. Use o módulo 'Contas a Pagar/Receber'.")

# --- MÓDULO FINANCEIRO ---
elif menu == "Contas a Pagar/Receber":
    st.header("💳 Movimentação")
    with st.form("lancamento"):
        c1, c2 = st.columns(2)
        data = c1.date_input("Data de Vencimento")
        desc = c2.text_input("Descrição")
        valor = c1.number_input("Valor R$", format="%.2f")
        tipo = c2.selectbox("Natureza", ["Pagar", "Receber"])
        status = st.selectbox("Status", ["Pendente", "Pago/Recebido"])
        
        if st.form_submit_button("Salvar Movimentação"):
            conn = sqlite3.connect('nanosignals_erp.db')
            conn.execute("INSERT INTO financeiro (data, descricao, valor, tipo, status) VALUES (?,?,?,?,?)", 
                         (data, desc, valor, tipo, status))
            conn.commit()
            conn.close()
            st.success("Lançamento efetuado!")
            st.rerun()
            
    st.divider()
    st.subheader("Lista de Movimentações")
    conn = sqlite3.connect('nanosignals_erp.db')
    st.dataframe(pd.read_sql_query("SELECT * FROM financeiro", conn), use_container_width=True)
    conn.close()

# --- MÓDULO CADASTROS ---
elif menu == "Cadastros":
    st.header("🏢 Cadastros")
    st.warning("Módulo em desenvolvimento. Aqui você cadastrará Bancos, Fornecedores e Planos de Conta.")
