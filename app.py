import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Configuração da Página
st.set_page_config(page_title="NanoSignals ERP", layout="wide")

# --- BANCO DE DADOS ROBUSTO ---
def get_db():
    conn = sqlite3.connect('nanosignals_erp.db', check_same_thread=False)
    # Estrutura com tabelas normalizadas
    conn.execute('''CREATE TABLE IF NOT EXISTS contas (id INTEGER PRIMARY KEY, nome TEXT, tipo TEXT, saldo REAL)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS financeiro (
                    id INTEGER PRIMARY KEY, data TEXT, valor REAL, descricao TEXT, 
                    conta_origem TEXT, categoria TEXT, tipo TEXT, status TEXT)''')
    return conn

# --- SIDEBAR DE NAVEGAÇÃO (Menus pedidos) ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/finance.png", width=60)
    st.title("NanoSignals ERP")
    menu = st.radio("MENU PRINCIPAL", ["Dashboard", "Financeiro / Movimentação", "Cadastros", "Relatórios", "Configurações"])

# --- DASHBOARD (Visualização) ---
if menu == "Dashboard":
    st.header("📊 Painel de Controle")
    st.info("Saldo Consolidado: R$ 0,00 | Próximos Vencimentos: 0")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Fluxo de Caixa")
        st.bar_chart(pd.DataFrame({'Entradas': [100, 200], 'Saídas': [50, 150]}))
    with col2:
        st.subheader("Curva ABC de Despesas")
        st.pie_chart(pd.DataFrame({'Valores': [500, 300, 200]}, index=['Fornecedor A', 'Fornecedor B', 'Impostos']))

# --- FINANCEIRO (Movimentação) ---
elif menu == "Financeiro / Movimentação":
    st.header("💳 Movimentação Financeira")
    tab1, tab2, tab3 = st.tabs(["Contas a Pagar", "Contas a Receber", "Transferências"])
    
    with tab1:
        st.subheader("Lançar Conta a Pagar")
        with st.form("pagar"):
            col1, col2 = st.columns(2)
            col1.date_input("Data Vencimento")
            col2.number_input("Valor R$", format="%.2f")
            st.text_input("Fornecedor")
            st.selectbox("Forma de Pagamento", ["Pix", "Cartão de Crédito", "Boleto", "TED"])
            if st.form_submit_button("Registrar Conta"):
                st.success("Conta registrada com sucesso!")

# --- CADASTROS ---
elif menu == "Cadastros":
    st.header("📝 Cadastros Base")
    cat = st.selectbox("O que deseja cadastrar?", ["Contas Bancárias", "Fornecedores", "Centro de Custo"])
    st.text_input(f"Nome do {cat}")
    st.button("Salvar Cadastro")

# --- RELATÓRIOS ---
elif menu == "Relatórios":
    st.header("📑 Central de Relatórios")
    st.multiselect("Filtrar por Período", ["Janeiro", "Fevereiro", "Março"])
    st.download_button("Exportar PDF", "dados", "relatorio.pdf")
