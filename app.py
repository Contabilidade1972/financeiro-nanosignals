import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="Gestão Financeira NanoSignals", layout="wide")

st.title("🚀 Sistema de Gestão Financeira - NanoSignals")

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRB94ZeKrMAp-UYBpTDrHRVKNfgF_3W9UCwVIQuntrQP7lq2Hd0DHWoWg0Qe8uWjQMoUFMDJ7oQgYrC/pub?output=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(url)
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce').dt.strftime('%d/%m/%Y')
    df['Valor'] = df['Valor'].fillna(0)
    df['Responsavel'] = df['Responsavel'].fillna('Não Definido')
    return df

df = load_data()

# Filtros Globais na Sidebar
st.sidebar.header("Filtros Avançados")
tipos = st.sidebar.multiselect("Filtrar por Tipo:", options=df['Tipo'].unique())
responsaveis = st.sidebar.multiselect("Filtrar por Sócio:", options=df['Responsavel'].unique())

if tipos: df = df[df['Tipo'].isin(tipos)]
if responsaveis: df = df[df['Responsavel'].isin(responsaveis)]

# Abas do Sistema
tab1, tab2, tab3 = st.tabs(["Dashboard Interativo", "Relatório Editável", "Novo Lançamento"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Evolução por Categoria")
        fig_bar = px.bar(df, x='Responsavel', y='Valor', color='Tipo', barmode='group')
        st.plotly_chart(fig_bar, use_container_width=True)
    with col2:
        st.subheader("Distribuição Financeira")
        fig_pie = px.pie(df, values='Valor', names='Responsavel', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.subheader("Edição Direta (Clique para editar)")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True, groupable=True)
    gb.configure_column("Valor", type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"], valueFormatter="data.Valor.toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'})")
    grid_options = gb.build()
    
    AgGrid(df, gridOptions=grid_options, update_mode=GridUpdateMode.VALUE_CHANGED)

with tab3:
    st.subheader("Cadastro Dinâmico")
    with st.form("form_novo"):
        novo_resp = st.text_input("Novo Responsável (se não estiver na lista):")
        lista_resp = df['Responsavel'].unique().tolist()
        if novo_resp: lista_resp.append(novo_resp)
        resp = st.selectbox("Responsável", options=lista_resp)
        # ... (restante do formulário) ...
        if st.form_submit_button("Registrar"):
            st.success(f"Registrado para {resp}")
