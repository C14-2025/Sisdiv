// script.js

// Variáveis globais
let sacData = [];
let priceData = [];
let sacChartInstance = null;
let priceChartInstance = null;
let comparisonChartInstance = null;

// Inicialização quando o documento estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Adicionar evento ao formulário (index.html)
    const form = document.getElementById('simulacaoForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            calcular();
        });
    }

    // Se já existem dados carregados (amortizacao.html), criar gráficos
    if (typeof sacData !== 'undefined' && (sacData.length > 0 || priceData.length > 0)) {
        criarResumos();
        criarGraficos();
    }
});

// Função para calcular a amortização
async function calcular() {
    const valor = parseFloat(document.getElementById('valor').value);
    const taxa = parseFloat(document.getElementById('taxa').value);
    const prazo = parseInt(document.getElementById('prazo').value);
    const carencia = parseInt(document.getElementById('carencia').value) || 0;
    const metodo = document.getElementById('metodo').value;
    const salvar = document.getElementById('salvar').checked;

    if (!valor || !taxa || !prazo) {
        alert('Por favor, preencha todos os campos obrigatórios!');
        return;
    }

    try {
        // Fazer requisição para o backend
        const formData = new FormData();
        formData.append('valor', valor);
        formData.append('taxa', taxa);
        formData.append('prazo', prazo);
        formData.append('carencia', carencia);
        formData.append('metodo', metodo);
        formData.append('salvar', salvar);

        const response = await fetch('/calcular/', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Erro no servidor: ' + response.status);
        }

        const data = await response.json();
        console.log('Dados recebidos:', data);

        // Processar os dados recebidos
        if (data.sac) {
            sacData = data.sac;
            criarTabelaSAC();
        }

        if (data.price) {
            priceData = data.price;
            criarTabelaPrice();
        }

        if (data.sac || data.price) {
            criarResumos();
            criarGraficos();
            document.getElementById('resultsSection').style.display = 'block';
        }

    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao calcular amortização. Verifique o console para mais detalhes.');
    }
}

// Funções para criar tabelas
function criarTabelaSAC() {
    const table = document.getElementById('sacTable');
    if (!table) return;

    let html = `
        <thead>
            <tr>
                <th>Parcela</th>
                <th>Prestação</th>
                <th>Juros</th>
                <th>Amortização</th>
                <th>Saldo Devedor</th>
            </tr>
        </thead>
        <tbody>
    `;

    sacData.forEach(row => {
        html += `
            <tr>
                <td>${row.parcela}</td>
                <td>R$ ${row.prestacao.toFixed(2)}</td>
                <td>R$ ${row.juros.toFixed(2)}</td>
                <td>R$ ${row.amortizacao.toFixed(2)}</td>
                <td>R$ ${row.saldo_devedor.toFixed(2)}</td>
            </tr>
        `;
    });

    html += '</tbody>';
    table.innerHTML = html;
}

function criarTabelaPrice() {
    const table = document.getElementById('priceTable');
    if (!table) return;

    let html = `
        <thead>
            <tr>
                <th>Parcela</th>
                <th>Prestação</th>
                <th>Juros</th>
                <th>Amortização</th>
                <th>Saldo Devedor</th>
            </tr>
        </thead>
        <tbody>
    `;

    priceData.forEach(row => {
        html += `
            <tr>
                <td>${row.parcela}</td>
                <td>R$ ${row.prestacao.toFixed(2)}</td>
                <td>R$ ${row.juros.toFixed(2)}</td>
                <td>R$ ${row.amortizacao.toFixed(2)}</td>
                <td>R$ ${row.saldo_devedor.toFixed(2)}</td>
            </tr>
        `;
    });

    html += '</tbody>';
    table.innerHTML = html;
}

// ------------------ Funções de Resumos e Gráficos ------------------

function criarResumos() {
    // Resumo SAC
    if (sacData.length > 0 && document.getElementById('sacSummary')) {
        const totalPrestacoesSAC = sacData.reduce((sum, row) => sum + row.prestacao, 0);
        const totalJurosSAC = sacData.reduce((sum, row) => sum + row.juros, 0);
        const totalAmortizacaoSAC = sacData.reduce((sum, row) => sum + row.amortizacao, 0);

        document.getElementById('sacSummary').innerHTML = `
            <div class="summary-card"><h3>Total de Prestações</h3><div class="value">R$ ${totalPrestacoesSAC.toFixed(2)}</div></div>
            <div class="summary-card"><h3>Total de Juros</h3><div class="value">R$ ${totalJurosSAC.toFixed(2)}</div></div>
            <div class="summary-card"><h3>Total Amortizado</h3><div class="value">R$ ${totalAmortizacaoSAC.toFixed(2)}</div></div>
            <div class="summary-card"><h3>Primeira Prestação</h3><div class="value">R$ ${sacData[0]?.prestacao.toFixed(2) || '0.00'}</div></div>
        `;
    }

    // Resumo Price
    if (priceData.length > 0 && document.getElementById('priceSummary')) {
        const totalPrestacoes = priceData.reduce((sum, row) => sum + row.prestacao, 0);
        const totalJuros = priceData.reduce((sum, row) => sum + row.juros, 0);
        const totalAmortizacao = priceData.reduce((sum, row) => sum + row.amortizacao, 0);

        document.getElementById('priceSummary').innerHTML = `
            <div class="summary-card"><h3>Total de Prestações</h3><div class="value">R$ ${totalPrestacoes.toFixed(2)}</div></div>
            <div class="summary-card"><h3>Total de Juros</h3><div class="value">R$ ${totalJuros.toFixed(2)}</div></div>
            <div class="summary-card"><h3>Total Amortizado</h3><div class="value">R$ ${totalAmortizacao.toFixed(2)}</div></div>
            <div class="summary-card"><h3>Prestação Fixa</h3><div class="value">R$ ${priceData.find(row => row.amortizacao > 0)?.prestacao.toFixed(2) || '0.00'}</div></div>
        `;
    }

    // Comparação
    if (sacData.length > 0 && priceData.length > 0 && document.getElementById('comparisonSummary')) {
        const totalPrestacoesSAC = sacData.reduce((sum, row) => sum + row.prestacao, 0);
        const totalJurosSAC = sacData.reduce((sum, row) => sum + row.juros, 0);
        const totalPrestacoesPrice = priceData.reduce((sum, row) => sum + row.prestacao, 0);
        const totalJurosPrice = priceData.reduce((sum, row) => sum + row.juros, 0);

        const economia = totalPrestacoesPrice - totalPrestacoesSAC;
        document.getElementById('comparisonSummary').innerHTML = `
            <div class="summary-card"><h3>Economia com SAC</h3><div class="value">R$ ${economia.toFixed(2)}</div></div>
            <div class="summary-card"><h3>Diferença de Juros</h3><div class="value">R$ ${(totalJurosPrice - totalJurosSAC).toFixed(2)}</div></div>
            <div class="summary-card"><h3>Melhor Método</h3><div class="value">${economia > 0 ? 'SAC' : 'Price'}</div></div>
        `;
    }
}

function criarGraficos() {
    // Gráfico SAC
    if (sacData.length > 0 && document.getElementById('sacChart')) {
        const ctxSAC = document.getElementById('sacChart').getContext('2d');
        // Remove anterior se ela existir
        if (sacChartInstance) {
            sacChartInstance.destroy();
        }
        sacChartInstance = new Chart(ctxSAC, {
            type: 'line',
            data: {
                labels: sacData.map(row => `Parcela ${row.parcela}`),
                datasets: [
                    { label: 'Prestação', data: sacData.map(row => row.prestacao), borderColor: '#667eea', backgroundColor: 'rgba(102, 126, 234, 0.1)', tension: 0.4 },
                    { label: 'Juros', data: sacData.map(row => row.juros), borderColor: '#ff6b6b', backgroundColor: 'rgba(255, 107, 107, 0.1)', tension: 0.4 },
                    { label: 'Amortização', data: sacData.map(row => row.amortizacao), borderColor: '#51cf66', backgroundColor: 'rgba(81, 207, 102, 0.1)', tension: 0.4 }
                ]
            },
            options: { responsive: true, plugins: { title: { display: true, text: 'Evolução das Parcelas - SAC' } } }
        });
    }

    // Gráfico Price
    if (priceData.length > 0 && document.getElementById('priceChart')) {
        const ctxPrice = document.getElementById('priceChart').getContext('2d');
        // Remove anterior se ela existir
        if (priceChartInstance) {
            priceChartInstance.destroy();
        }
        priceChartInstance = new Chart(ctxPrice, {
            type: 'line',
            data: {
                labels: priceData.map(row => `Parcela ${row.parcela}`),
                datasets: [
                    { label: 'Prestação', data: priceData.map(row => row.prestacao), borderColor: '#667eea', backgroundColor: 'rgba(102, 126, 234, 0.1)', tension: 0.4 },
                    { label: 'Juros', data: priceData.map(row => row.juros), borderColor: '#ff6b6b', backgroundColor: 'rgba(255, 107, 107, 0.1)', tension: 0.4 },
                    { label: 'Amortização', data: priceData.map(row => row.amortizacao), borderColor: '#51cf66', backgroundColor: 'rgba(81, 207, 102, 0.1)', tension: 0.4 }
                ]
            },
            options: { responsive: true, plugins: { title: { display: true, text: 'Evolução das Parcelas - Price' } } }
        });
    }

    // Gráfico Comparação
    if (sacData.length > 0 && priceData.length > 0 && document.getElementById('comparisonChart')) {
        const ctxComparison = document.getElementById('comparisonChart').getContext('2d');
        // Remove anterior se ela existir
        if (comparisonChartInstance) {
            comparisonChartInstance.destroy();
        }
        comparisonChartInstance = new Chart(ctxComparison, {
            type: 'bar',
            data: {
                labels: ['Total Prestações', 'Total Juros', 'Total Amortização'],
                datasets: [
                    { label: 'SAC', data: [sacData.reduce((s, r) => s + r.prestacao, 0), sacData.reduce((s, r) => s + r.juros, 0), sacData.reduce((s, r) => s + r.amortizacao, 0)], backgroundColor: 'rgba(102, 126, 234, 0.8)' },
                    { label: 'Price', data: [priceData.reduce((s, r) => s + r.prestacao, 0), priceData.reduce((s, r) => s + r.juros, 0), priceData.reduce((s, r) => s + r.amortizacao, 0)], backgroundColor: 'rgba(255, 107, 107, 0.8)' }
                ]
            },
            options: { responsive: true, plugins: { title: { display: true, text: 'Comparação SAC vs Price' } } }
        });
    }
}

// Alternar abas
function showTab(tabName) {
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    event.target.classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');
}

// Funções de exportação
function exportToCSV(tipo) {
    let data = tipo === 'sac' ? sacData : priceData;
    if (!data.length) return;

    let csv = "Parcela,Prestação,Juros,Amortização,Saldo Devedor\n";
    data.forEach(row => {
        csv += `${row.parcela},${row.prestacao.toFixed(2)},${row.juros.toFixed(2)},${row.amortizacao.toFixed(2)},${row.saldo_devedor.toFixed(2)}\n`;
    });

    let blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    let link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `${tipo}_amortizacao.csv`;
    link.click();
}

function exportToPDF(tipo) {
    let { jsPDF } = window.jspdf;
    let doc = new jsPDF();
    let data = tipo === 'sac' ? sacData : priceData;
    if (!data.length) return;

    doc.text(`Tabela ${tipo.toUpperCase()} - Amortização`, 10, 10);
    let y = 20;
    data.forEach(row => {
        doc.text(`${row.parcela} | R$ ${row.prestacao.toFixed(2)} | R$ ${row.juros.toFixed(2)} | R$ ${row.amortizacao.toFixed(2)} | R$ ${row.saldo_devedor.toFixed(2)}`, 10, y);
        y += 10;
    });
    doc.save(`${tipo}_amortizacao.pdf`);
}

// Limpar campos do formulário
function limparCampos() {
    document.getElementById('simulacaoForm').reset();
    document.getElementById('resultsSection').style.display = 'none';
}
