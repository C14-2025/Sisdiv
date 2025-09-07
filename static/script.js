// Variáveis globais
let sacData = [];
let priceData = [];

// Inicialização quando o documento estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Adicionar evento ao formulário
    const form = document.getElementById('simulacaoForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            calcular();
        });
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

// As funções criarResumos(), criarGraficos(), showTab(), exportToCSV(), exportToPDF() e limparCampos()
// devem ser mantidas conforme o código original fornecido anteriormente
