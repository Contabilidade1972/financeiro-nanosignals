import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="NanoSignals PRO", layout="wide")

# CSS para forçar um layout limpo e profissional
st.markdown("""
    <style>
    .stMetric {background-color: #f0f2f6; padding: 15px; border-radius: 10px;}
    .css-1544g2n {padding: 1rem;}
    </style>
""", unsafe_allow_html=True)

# Banco de Dados
def get_db():
    return sqlite3.connect('nanosignals_pro.db', check_same_thread=False)

# Menu Superior limpo
menu = st.radio("Selecione o Módulo:", ["Dashboard Executivo", "Movimentação Financeira"], horizontal=True)

if menu == "Dashboard Executivo":
    st.title("📊 Painel NanoSignals")
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM financeiro", conn)
    conn.close()

    if not df.empty:
        # Limpeza forçada dos dados para evitar o erro visual
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Entradas", f"R$ {df[df['tipo']=='Entrada']['valor'].sum():,.2f}")
        c2.metric("Saídas", f"R$ {df[df['tipo']=='Saída']['valor'].sum():,.2f}")
        c3.metric("Saldo", f"R$ {df[df['tipo']=='Entrada']['valor'].sum() - df[df['tipo']=='Saída']['valor'].sum():,.2f}")
        
        st.divider()
        st.plotly_chart(px.bar(df, x='descricao', y='valor', color='tipo', title="Distribuição de Fluxo"), use_container_width=True)
    else:
        st.warning("Nenhum dado registrado. Vá para 'Movimentação Financeira'.")

else:
    st.title("📝 Gestão de Movimentação")
    with st.form("lancamento"):
        c1, c2 = st.columns(2)
        data = c1.date_input("Data")
        valor = c2.number_input("Valor R$", format="%.2f")
        desc = c1.text_input("Descrição")
        tipo = c2.selectbox("Tipo", ["Entrada", "Saída"])
        if st.form_submit_button("Confirmar Lançamento"):
            conn = get_db()
            conn.execute("INSERT INTO financeiro (data, valor, descricao, tipo) VALUES (?,?,?,?)", 
                         (str(data), valor, desc, tipo))
            conn.commit()
            conn.close()
            st.rerun()
            
    # Listagem organizada
    conn = get_db()
    st.dataframe(pd.read_sql_query("SELECT * FROM financeiro", conn), use_container_width=True)
    conn.close()
