import streamlit as st
import streamlit.components.v1 as components

# Configuração para tela cheia
st.set_page_config(layout="wide")

# O seu código HTML/CSS/JS profissional inserido aqui
html_code = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: sans-serif; background: #f8fafc; }
        .container { padding: 20px; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="container">
        <h1>NanoSignals ERP</h1>
        <div class="card">
            <p>Sistema Financeiro Profissional Carregado</p>
        </div>
    </div>
</body>
</html>
"""

# Renderiza o HTML dentro do Streamlit
components.html(html_code, height=800)
