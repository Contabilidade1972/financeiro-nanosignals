<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>NanoSignals ERP - Sistema Financeiro</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        /* Estilo base profissional */
        body { font-family: 'Inter', sans-serif; background: #f8fafc; margin: 0; display: flex; }
        .sidebar { width: 260px; height: 100vh; background: #0f172a; color: #fff; position: fixed; padding: 20px; }
        .main { margin-left: 260px; width: 100%; padding: 30px; }
        .card { background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .grid-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        .stat-card { padding: 20px; background: #fff; border-radius: 10px; border: 1px solid #e2e8f0; }
        .btn { padding: 10px 20px; border-radius: 6px; border: none; cursor: pointer; color: white; background: #1a56db; }
    </style>
</head>
<body>

<aside class="sidebar">
    <h2>NanoSignals ERP</h2>
    <nav>
        <div onclick="showPage('dashboard')" style="cursor:pointer; padding: 10px;">Dashboard</div>
        <div onclick="showPage('financeiro')" style="cursor:pointer; padding: 10px;">Financeiro</div>
    </nav>
</aside>

<main class="main" id="content">
    <div id="dashboard">
        <h1>Dashboard</h1>
        <div class="grid-stats">
            <div class="stat-card">Saldo Consolidado: <br><strong id="saldoVal">R$ 0,00</strong></div>
        </div>
        <canvas id="meuGrafico" width="400" height="100"></canvas>
    </div>
    
    <div id="financeiro" style="display:none;">
        <h1>Financeiro</h1>
        <div class="card">
            <input type="date" id="data">
            <input type="text" id="desc" placeholder="Descrição">
            <input type="number" id="valor" placeholder="Valor">
            <select id="tipo"><option value="Receber">Receber</option><option value="Pagar">Pagar</option></select>
            <button class="btn" onclick="salvarLancamento()">Salvar</button>
        </div>
        <table id="tabelaDados" style="width:100%">
            <thead><tr><th>Data</th><th>Descricao</th><th>Valor</th><th>Tipo</th></tr></thead>
            <tbody></tbody>
        </table>
    </div>
</main>

<script>
    let dados = JSON.parse(localStorage.getItem('ns_dados')) || [];

    function showPage(page) {
        document.getElementById('dashboard').style.display = page === 'dashboard' ? 'block' : 'none';
        document.getElementById('financeiro').style.display = page === 'financeiro' ? 'block' : 'none';
    }

    function salvarLancamento() {
        let lancamento = {
            data: document.getElementById('data').value,
            desc: document.getElementById('desc').value,
            valor: parseFloat(document.getElementById('valor').value),
            tipo: document.getElementById('tipo').value
        };
        dados.push(lancamento);
        localStorage.setItem('ns_dados', JSON.stringify(dados));
        renderTabela();
        alert('Salvo com sucesso!');
    }

    function renderTabela() {
        let tbody = document.querySelector('#tabelaDados tbody');
        tbody.innerHTML = '';
        dados.forEach(d => {
            tbody.innerHTML += `<tr><td>${d.data}</td><td>${d.desc}</td><td>${d.valor}</td><td>${d.tipo}</td></tr>`;
        });
        atualizarDashboard();
    }

    function atualizarDashboard() {
        let saldo = dados.reduce((acc, d) => d.tipo === 'Receber' ? acc + d.valor : acc - d.valor, 0);
        document.getElementById('saldoVal').textContent = 'R$ ' + saldo.toFixed(2);
    }

    renderTabela();
</script>
</body>
</html>
