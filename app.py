import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="Gestão Financeira NanoSignals", layout="wide")

st.title("📊 Sistema de Gestão Financeira - NanoSignals")

# URL da planilha consolidada (após a publicação)
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRB94ZeKrMAp-UYBpTDrHRVKNfgF_3W9UCwVIQuntrQP7lq2Hd0DHWoWg0Qe8uWjQMoUFMDJ7oQgYrC/pub?output=csv"

@st.cache_data
def carregar_dados():
    df = pd.read_csv(url)
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce').dt.strftime('%d/%m/%Y')
    df['Valor'] = df['Valor'].fillna(0)
    df['Responsavel'] = df['Responsavel'].fillna('Não Definido')
    return df

df = carregar_dados()

# Barra Lateral - Filtros
st.sidebar.header("Filtros de Análise")
tipos = st.sidebar.multiselect("Filtrar por Tipo:", options=df['Tipo'].unique())
responsaveis = st.sidebar.multiselect("Filtrar por Sócio:", options=df['Responsavel'].unique())

if tipos: df = df[df['Tipo'].isin(tipos)]
if responsaveis: df = df[df['Responsavel'].isin(responsaveis)]

# Abas Principais
aba1, aba2, aba3 = st.tabs(["Dashboard Interativo", "Relatório Detalhado", "Novo Lançamento"])

with aba1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Evolução por Sócio")
        fig_bar = px.bar(df, x='Responsavel', y='Valor', color='Tipo', barmode='group', labels={'Responsavel': 'Sócio', 'Valor': 'Valor (R$)'})
        st.plotly_chart(fig_bar, use_container_width=True)
    with col2:
        st.subheader("Distribuição do Fluxo")
        fig_pie = px.pie(df, values='Valor', names='Responsavel', hole=0.4, labels={'Responsavel': 'Sócio'})
        st.plotly_chart(fig_pie, use_container_width=True)

with aba2:
    st.subheader("Relatório Financeiro Editável")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True, groupable=True, filter=True)
    gb.configure_column("Valor", type=["numericColumn", "numberColumnFilter"], valueFormatter="value.toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'})")
    grid_options = gb.build()
    
    AgGrid(df, gridOptions=grid_options, update_mode=GridUpdateMode.VALUE_CHANGED, theme='streamlit')

with aba3:
    st.subheader("Novo Registro de Lançamento")
    with st.form("form_registro"):
        data = st.date_input("Data do Lançamento")
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        descricao = st.text_input("Descrição do Movimento")
        resp_list = df['Responsavel'].unique().tolist()
        resp = st.selectbox("Responsável", options=resp_list + ["Adicionar novo..."])
        if resp == "Adicionar novo...":
            resp = st.text_input("Nome do novo sócio/responsável")
        tipo = st.radio("Natureza da operação:", ["Entrada", "Saída"])
        
        if st.form_submit_button("Confirmar Lançamento"):
            st.success(f"Registro de {tipo} no valor de R$ {valor:.2f} processado!")
