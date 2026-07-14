import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Configuração da página
st.set_page_config(page_title="NanoSignals PRO", layout="wide")
st.title("🚀 NanoSignals - Gestão Autônoma e Integrada")

# Conexão com o banco de dados interno
conn = sqlite3.connect('nanosignals_db.db', check_same_thread=False)
c = conn.cursor()

# Criação da tabela padrão (Data, Valor, Descricao, Responsavel, Tipo)
c.execute('''CREATE TABLE IF NOT EXISTS financeiro 
             (data TEXT, valor REAL, descricao TEXT, responsavel TEXT, tipo TEXT)''')
conn.commit()

# --- MÓDULO DE MIGRACÃO AUTOMÁTICA ---
def importar_csv_para_banco():
    arquivos = [f for f in os.listdir('.') if f.endswith('.csv')]
    for arquivo in arquivos:
        try:
            df = pd.read_csv(arquivo)
            # Renomeia colunas para garantir consistência
            df.columns = ['data', 'valor', 'descricao', 'responsavel', 'tipo']
            df.to_sql('financeiro', conn, if_exists='append', index=False)
        except Exception as e:
            st.warning(f"Erro ao importar {arquivo}: {e}")
    conn.commit()

# Verifica se o banco está vazio para importar as planilhas
c.execute("SELECT count(*) FROM financeiro")
if c.fetchone()[0] == 0:
    importar_csv_para_banco()
    st.info("Sistema inicializado: Histórico das planilhas importado.")

# --- INTERFACE ---
aba1, aba2, aba3 = st.tabs(["Dashboard", "Gestão de Dados", "Novo Lançamento"])

# Carrega dataframe do banco
df_banco = pd.read_sql_query("SELECT * FROM financeiro", conn)

with aba1:
    st.subheader("Visão Geral Financeira")
    col1, col2 = st.columns(2)
    if not df_banco.empty:
        col1.plotly_chart(px.bar(df_banco, x='responsavel', y='valor', color='tipo', title="Gastos por Sócio"), use_container_width=True)
        col2.plotly_chart(px.pie(df_banco, values='valor', names='responsavel', title="Distribuição"), use_container_width=True)

with aba2:
    st.subheader("Relatórios Detalhados")
    gb = GridOptionsBuilder.from_dataframe(df_banco)
    gb.configure_default_column(editable=True, filter=True)
    AgGrid(df_banco, gridOptions=gb.build(), update_mode=GridUpdateMode.VALUE_CHANGED, use_container_width=True)
    
    if st.button("Download CSV"):
        st.download_button("Clique aqui para baixar o relatório", data=df_banco.to_csv(index=False), file_name="relatorio_nanosignals.csv")

with aba3:
    st.subheader("Novo Registro de Lançamento")
    with st.form("form_novo"):
        data = st.date_input("Data do lançamento")
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        desc = st.text_input("Descrição")
        resp = st.text_input("Responsável")
        tipo = st.selectbox("Tipo de movimento", ["Entrada", "Saída"])
        
        if st.form_submit_button("Salvar no Sistema"):
            c.execute("INSERT INTO financeiro VALUES (?,?,?,?,?)", (str(data), valor, desc, resp, tipo))
            conn.commit()
            st.success("Lançamento salvo com sucesso!")
            st.rerun()
