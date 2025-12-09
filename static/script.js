// script.js

// Variáveis globais
let sacData = [];
let priceData = [];
let samData = [];

let sacChartInstance = null;
let priceChartInstance = null;
let samChartInstance = null;
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

    // Adicionando evento ao formulário de investimentos (investimentos.html)
    const form2 = document.getElementById('investForm');
    if (form2) {
        form2.addEventListener('submit', function(e) {
            e.preventDefault()
            simularInvestimentos();
        });
    }
    
    // Se já existem dados carregados (amortizacao.html), criar gráficos
    if (typeof sacData !== 'undefined' && (sacData.length > 0 || priceData.length > 0 || samData.length > 0 || pagamento_variavelData.length > 0)) {
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
    const salvar = false;

    if (!valor || !taxa || !prazo) {
        alert('Por favor, preencha todos os campos obrigatórios!');
        return;
    }

    const formData = new FormData();
    formData.append('valor', valor);
    formData.append('taxa', taxa);
    formData.append('prazo', prazo);
    formData.append('carencia', carencia);
    formData.append('metodo', metodo);

    try {
        // Fazer requisição para o backend
        const response = await fetch('/calcular/', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error('Erro no servidor: ' + (errorData.detail || response.status));
        }

        const data = await response.json();
        console.log('Dados recebidos:', data);

        // Processar os dados recebidos (CORRIGIDO: usa as variáveis globais)
        if (data.sac) {
            sacData = data.sac;
            criarTabelaSAC();
        } else {
            sacData = []; // Limpa
        }

        if (data.price) {
            priceData = data.price;
            criarTabelaPrice();
        } else {
            priceData = []; // Limpa
        }

        if (data.sam) {
            samData = data.sam;
            criarTabelaSAM();
        } else {
            samData = []; // Limpa
        }

        // Criar resumos e gráficos se houver dados
        if (sacData.length > 0 || priceData.length > 0 || samData.length > 0) {
            criarResumos();
            criarGraficos();
            document.getElementById('resultsSection').style.display = 'block';

            // Ativa a primeira aba disponível
            let defaultTab = sacData.length > 0 ? 'sac' : priceData.length > 0 ? 'price' : samData.length > 0 ? 'sam' : 'pagamento_variavel';
            showTab(defaultTab);
        } else {
             document.getElementById('resultsSection').style.display = 'none';
        }

    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao calcular amortização. Verifique o console para mais detalhes.');
    }
}

// Função para calcular a simulação dos investimentos
async function simularInvestimentos() {
    // puxando a entrada do usuário do HTML
    const tipo = document.getElementById('tipo').value;
    const percentual_base = parseFloat(document.getElementById('percentual_base').value);
    const prazo_anos = parseInt(document.getElementById('prazo_anos').value);
    const valor_investido = parseFloat(document.getElementById('valor_investido').value);
    const taxa_atual_selic = parseFloat(document.getElementById('taxa_atual_selic').value);

    // taxa atual selic é opcional porque pode ser puxada da API do banco central
    // verificando se todos os campos obrigatórios foram preenchidos
    if (!tipo || !percentual_base || !prazo_anos || ! valor_investido){
        alert('Por favor, preencha todos os campos obrigatórios!');
        return;
    }

    const formData = new FormData();
    formData.append('tipo', tipo)
    formData.append('percentual_base', percentual_base)
    formData.append('prazo_anos', prazo_anos)
    formData.append('valor_investido', valor_investido)
    formData.append('taxa_atual_selic', taxa_atual_selic)
    
    try{
        const response = await fetch('/investimentos/', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error('Erro no servidor: ' + (errorData.detail || response.status));
        }

        const data = await response.json();
        console.log('Dados recebidos:', data);

        // Mostrando na página
        document.getElementById('resultsSection').style.display = 'block'
        
        document.getElementById('rentabilidade').innerText = data['rentabilidade_total_percentual'].toFixed(2);
        document.getElementById('valor_final').innerText = data['valor_final'].toFixed(2);

    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao calcular seus investimentos. Verifique o console para mais detalhes.');
    }
}

// Funções para criar tabelas (mantidas inalteradas)
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
                <td>R$ ${row.prestacao.toFixed(2).replace('.', ',')}</td>
                <td>R$ ${row.juros.toFixed(2).replace('.', ',')}</td>
                <td>R$ ${row.amortizacao.toFixed(2).replace('.', ',')}</td>
                <td>R$ ${row.saldo_devedor.toFixed(2).replace('.', ',')}</td>
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
                <td>R$ ${row.prestacao.toFixed(2).replace('.', ',')}</td>
                <td>R$ ${row.juros.toFixed(2).replace('.', ',')}</td>
                <td>R$ ${row.amortizacao.toFixed(2).replace('.', ',')}</td>
                <td>R$ ${row.saldo_devedor.toFixed(2).replace('.', ',')}</td>
            </tr>
        `;
    });

    html += '</tbody>';
    table.innerHTML = html;
}

function criarTabelaSAM() {
    const table = document.getElementById('samTable');
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

    samData.forEach(row => {
        html += `
            <tr>
                <td>${row.parcela}</td>
                <td>R$ ${row.prestacao.toFixed(2).replace('.', ',')}</td>
                <td>R$ ${row.juros.toFixed(2).replace('.', ',')}</td>
                <td>R$ ${row.amortizacao.toFixed(2).replace('.', ',')}</td>
                <td>R$ ${row.saldo_devedor.toFixed(2).replace('.', ',')}</td>
            </tr>
        `;
    });

    html += '</tbody>';
    table.innerHTML = html;
}

// ------------------ Funções de Resumos e Gráficos ------------------

function criarResumos() {
    // Função auxiliar para criar card de resumo
    function createSummaryCards(data, summaryId, fixedLabel) {
        if (!data || data.length === 0 || !document.getElementById(summaryId)) return;

        const totalPrestacoes = data.reduce((sum, row) => sum + row.prestacao, 0);
        const totalJuros = data.reduce((sum, row) => sum + row.juros, 0);
        const totalAmortizacao = data.reduce((sum, row) => sum + row.amortizacao, 0);

        const firstValue = data.find(row => row.amortizacao > 0 || row.prestacao > 0)?.prestacao.toFixed(2).replace('.', ',') || '0.00';

        document.getElementById(summaryId).innerHTML = `
            <div class="summary-card"><h3>Total de Prestações</h3><div class="value">R$ ${totalPrestacoes.toFixed(2).replace('.', ',')}</div></div>
            <div class="summary-card"><h3>Total de Juros</h3><div class="value">R$ ${totalJuros.toFixed(2).replace('.', ',')}</div></div>
            <div class="summary-card"><h3>Total Amortizado</h3><div class="value">R$ ${totalAmortizacao.toFixed(2).replace('.', ',')}</div></div>
            <div class="summary-card"><h3>${fixedLabel}</h3><div class="value">R$ ${firstValue}</div></div>
        `;
    }

    // Resumos Individuais
    createSummaryCards(sacData, 'sacSummary', 'Primeira Prestação');
    createSummaryCards(priceData, 'priceSummary', 'Prestação Fixa');
    createSummaryCards(samData, 'samSummary', 'Prestação Juros');


    // **CORREÇÃO:** Comparação APENAS SAC vs Price, e só exibe se ambos existirem
    const comparisonSummary = document.getElementById('comparisonSummary');
    if (comparisonSummary && sacData.length > 0 && priceData.length > 0) {

        const totalPrestacoesSAC = sacData.reduce((sum, row) => sum + row.prestacao, 0);
        const totalJurosSAC = sacData.reduce((sum, row) => sum + row.juros, 0);
        const totalPrestacoesPrice = priceData.reduce((sum, row) => sum + row.prestacao, 0);
        const totalJurosPrice = priceData.reduce((sum, row) => sum + row.juros, 0);

        // Se o Price for maior que o SAC em prestações totais, a economia com SAC é positiva.
        const economia = totalPrestacoesPrice - totalPrestacoesSAC;
        const melhorMetodo = totalPrestacoesSAC < totalPrestacoesPrice ? 'SAC' : (totalPrestacoesPrice < totalPrestacoesSAC ? 'Price' : 'Empate');

        comparisonSummary.innerHTML = `
            <div class="summary-card"><h3>SAC Juros Totais</h3><div class="value">R$ ${totalJurosSAC.toFixed(2).replace('.', ',')}</div></div>
            <div class="summary-card"><h3>Price Juros Totais</h3><div class="value">R$ ${totalJurosPrice.toFixed(2).replace('.', ',')}</div></div>
            <div class="summary-card"><h3>Melhor Método (Menor Juros)</h3><div class="value">${melhorMetodo}</div></div>
        `;
    } else if (comparisonSummary) {
         // Garante que a seção de comparação limpa se não tiver os dois, para atender a regra de "não quero o sac sozinho ou price sozinho".
         comparisonSummary.innerHTML = '<h2>Comparação</h2><p>Calcule os métodos SAC e Price para ver a comparação detalhada.</p>';
    }
}

function criarGraficos() {
    // Gráfico SAC
    if (sacData.length > 0 && document.getElementById('sacChart')) {
        const ctxSAC = document.getElementById('sacChart').getContext('2d');
        if (sacChartInstance) { sacChartInstance.destroy(); }
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
        if (priceChartInstance) { priceChartInstance.destroy(); }
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

    // Gráfico SAM (Mantido)
    if (samData.length > 0 && document.getElementById('samChart')) {
        const ctxSAM = document.getElementById('samChart').getContext('2d');
        if (samChartInstance) { samChartInstance.destroy(); }
        samChartInstance = new Chart(ctxSAM, {
            type: 'line',
            data: {
                labels: samData.map(row => `Parcela ${row.parcela}`),
                datasets: [
                    { label: 'Prestação', data: samData.map(row => row.prestacao), borderColor: '#3498db', backgroundColor: 'rgba(52, 152, 219, 0.1)', tension: 0.4 },
                    { label: 'Juros', data: samData.map(row => row.juros), borderColor: '#e74c3c', backgroundColor: 'rgba(231, 76, 60, 0.1)', tension: 0.4 },
                    { label: 'Amortização', data: samData.map(row => row.amortizacao), borderColor: '#2ecc71', backgroundColor: 'rgba(46, 204, 113, 0.1)', tension: 0.4 }
                ]
            },
            options: { responsive: true, plugins: { title: { display: true, text: 'Evolução das Parcelas - SAM' } } }
        });
    }

    // **CORREÇÃO:** Gráfico Comparação SAC vs Price (APENAS SAC e Price, Título Fixo)
    if (document.getElementById('comparisonChart') && sacData.length > 0 && priceData.length > 0) {
        const datasets = [];
        const labels = ['Total Prestações', 'Total Juros', 'Total Amortização'];

        // APENAS adiciona SAC e Price nos datasets
        datasets.push({ label: 'SAC', data: [sacData.reduce((s, r) => s + r.prestacao, 0), sacData.reduce((s, r) => s + r.juros, 0), sacData.reduce((s, r) => s + r.amortizacao, 0)], backgroundColor: 'rgba(102, 126, 234, 0.8)' });
        datasets.push({ label: 'Price', data: [priceData.reduce((s, r) => s + r.prestacao, 0), priceData.reduce((s, r) => s + r.juros, 0), priceData.reduce((s, r) => s + r.amortizacao, 0)], backgroundColor: 'rgba(255, 107, 107, 0.8)' });

        // Cria o gráfico
        const ctxComparison = document.getElementById('comparisonChart').getContext('2d');
        if (comparisonChartInstance) {
            comparisonChartInstance.destroy();
        }
        comparisonChartInstance = new Chart(ctxComparison, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Comparação SAC vs Price' // Título fixo conforme solicitação
                    }
                }
            }
        });
    } else if (comparisonChartInstance) {
        // Destrói o gráfico se ele existe, mas a condição (SAC E Price) não é satisfeita.
        comparisonChartInstance.destroy();
        comparisonChartInstance = null;
    }
}

// Alternar abas
function showTab(tabName) {
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.style.display = 'none');

    const targetButton = document.querySelector(`.tab-button[onclick="showTab('${tabName}')"]`);
    const targetContent = document.getElementById(`${tabName}-tab`);

    if (targetButton) {
        targetButton.classList.add('active');
    }
    if (targetContent) {
        targetContent.style.display = 'block';
    }
}

// Funções de exportação
function exportToCSV(tipo) {
    let data;
    switch (tipo) {
        case 'sac': data = sacData; break;
        case 'price': data = priceData; break;
        case 'sam': data = samData; break;
        case 'pagamento_variavel': data = pagamento_variavelData; break;
        default: return;
    }

    if (!data.length) return;

    let csv = "Parcela,Prestação,Juros,Amortização,Saldo Devedor\n";
    data.forEach(row => {
        csv += `${row.parcela},${row.prestacao.toFixed(2).replace('.', ',')},${row.juros.toFixed(2).replace('.', ',')},${row.amortizacao.toFixed(2).replace('.', ',')},${row.saldo_devedor.toFixed(2).replace('.', ',')}\n`;
    });

    let blob = new Blob(["\ufeff" + csv], { type: "text/csv;charset=utf-8;" });
    let link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `${tipo}_amortizacao.csv`;
    link.click();
}

function exportToPDF(tipo) {
    let { jsPDF } = window.jspdf;
    let doc = new jsPDF();
    let data;
    let titulo;

    switch (tipo) {
        case 'sac': data = sacData; titulo = 'SAC'; break;
        case 'price': data = priceData; titulo = 'PRICE'; break;
        case 'sam': data = samData; titulo = 'SAM'; break;
        case 'pagamento_variavel': data = pagamento_variavelData; titulo = 'PAGAMENTO VARIAVEL'; break;
        default: return;
    }

    if (!data.length) return;

    doc.setFontSize(16);
    doc.text(`Tabela ${titulo} - Amortização`, 14, 15);

    const headers = [
        ["Parcela", "Prestação", "Juros", "Amortização", "Saldo Devedor"]
    ];

    const rows = data.map(row => [
        row.parcela,
        `R$ ${row.prestacao.toFixed(2).replace('.', ',')}`,
        `R$ ${row.juros.toFixed(2).replace('.', ',')}`,
        `R$ ${row.amortizacao.toFixed(2).replace('.', ',')}`,
        `R$ ${row.saldo_devedor.toFixed(2).replace('.', ',')}`
    ]);

    doc.autoTable({
        startY: 25,
        head: headers,
        body: rows,
        styles: {
            fontSize: 10,
            cellPadding: 4
        },
        headStyles: {
            fillColor: [102, 126, 234],
            textColor: 255,
            halign: 'center'
        },
        alternateRowStyles: {
            fillColor: [240, 240, 240]
        },
        margin: { left: 14, right: 14 },
    });

    doc.save(`${tipo}_amortizacao.pdf`);
}

// Limpar campos do formulário
function limparCampos() {
    document.getElementById('simulacaoForm').reset();
    document.getElementById('resultsSection').style.display = 'none';
    if (typeof toggleAmortizacoesInput === 'function') {
        toggleAmortizacoesInput();
    }
}

// função para limpar os campos do formulário de investimentos
function limparCamposInvest() {
    document.getElementById('investForm').reset();
    document.getElementById('resultsSection').style.display = 'none';
}

async function salvarSimulacao() {
    const valor = parseFloat(document.getElementById('valor').value);
    const taxa = parseFloat(document.getElementById('taxa').value);
    const prazo = parseInt(document.getElementById('prazo').value);
    const carencia = parseInt(document.getElementById('carencia').value) || 0;
    const metodo = document.getElementById('metodo').value;

    const formData = new FormData();
    formData.append('valor', valor);
    formData.append('taxa', taxa);
    formData.append('prazo', prazo);
    formData.append('carencia', carencia);
    formData.append('metodo', metodo);

    try {
        const response = await fetch("/salvar_simulacao", {
            method: "POST",
            body: formData
        });

        if (response.redirected) {
            window.location.href = response.url;
            return;
        }

        if (response.ok) {
            alert("Simulação salva com sucesso!");
        } else {
             const data = await response.json();
             alert(`Erro ao salvar simulação: ${data.detail || 'Ocorreu um erro desconhecido.'}`);
        }

    } catch (err) {
        console.error(err);
        alert("Erro ao conectar ao servidor.");
    }
}
