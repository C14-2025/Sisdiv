import pytest
import sys
import os
from unittest.mock import patch
from fastapi.testclient import TestClient

# Adiciona o diretório raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa funções de cálculo
from calcular_sac import calcular_sac
from calcular_price import calcular_price
from calculo_pagamento_variavel import calculo_pagamento_variavel

# Importa a aplicação FastAPI
from main import app

# Cliente de teste para simular requisições HTTP
client = TestClient(app)

def formatar_brl(valor):
    """Formata valores no padrão brasileiro R$ 1.000,00"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class TestAmortizacao:
    """Classe de testes unitários para o sistema de amortização"""

    # ----------------- Testes de rotas da API -----------------
    def test_homepage_html(self):
        """Verifica se a página inicial carrega corretamente"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_simulacoes_html(self):
        """Verifica se a página de simulações carrega corretamente"""
        response = client.get("/simulacoes/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_calculo_json_response(self):
        """Testa la rota de cálculo e verifica se retorna JSON válido"""
        response = client.post("/calcular/", data={
            "valor": 10000,
            "taxa": 5,
            "prazo": 12,
            "carencia": 0,
            "metodo": "sac",
            "salvar": False
        })
        assert response.status_code == 200
        data = response.json()
        assert "sac" in data
        assert isinstance(data["sac"], list)
        assert all("prestacao" in p for p in data["sac"])

    def test_simulacao_nao_encontrada(self):
        """Verifica se o sistema lida corretamente com simulação inexistente"""
        response = client.get("/simulacao/999999")
        assert response.status_code == 200
        assert "Simulação não encontrada" in response.text

    # ----------------- Testes de cálculos -----------------
    def test_comparativo_sac_vs_price_total_pago(self):
        """Comparação SAC vs Price: SAC deve ser mais vantajoso"""
        valor = 100000
        taxa = 0.01
        prazo = 12

        sac = calcular_sac(valor, taxa, prazo)
        price = calcular_price(valor, taxa, prazo)

        total_sac = sum(p['prestacao'] for p in sac)
        total_price = sum(p['prestacao'] for p in price)

        # SAC geralmente tem menor total pago
        assert total_sac < total_price
        assert total_sac == pytest.approx(106500.0, 0.1)
        assert total_price == pytest.approx(106618.55, 0.1)

    def test_sac_valor_zero(self):
        """Empréstimo = 0 deve gerar erro"""
        valor = 0
        taxa = 0.01
        prazo = 12
        with pytest.raises(Exception):
            calcular_sac(valor, taxa, prazo)

    def test_price_prazo_negativo(self):
        """Prazo negativo deve gerar erro"""
        valor = 100000
        taxa = 0.01
        prazo = -5
        with pytest.raises(Exception):
            calcular_price(valor, taxa, prazo)

    def test_sac_taxa_negativa(self):
        """Taxa negativa deve gerar erro"""
        valor = 100000
        taxa = -0.01
        prazo = 12
        with pytest.raises(Exception):
            calcular_sac(valor, taxa, prazo)

    def test_sac_com_carencia(self):
        """Testa SAC com carência: parcelas iniciais só juros"""
        valor = 10000
        taxa = 0.02
        prazo = 6
        carencia = 2
        sac = calcular_sac(valor, taxa, prazo, carencia)
        for i in range(carencia):
            assert sac[i]['prestacao'] == sac[i]['juros']
        for i in range(carencia, prazo):
            assert sac[i]['prestacao'] > sac[i]['juros']

    def test_price_valor_muito_alto(self):
        """Testa Price com valor muito alto sem overflow"""
        valor = 1_000_000_000
        taxa = 0.01
        prazo = 12
        price = calcular_price(valor, taxa, prazo)
        assert len(price) == prazo
        assert all(p['prestacao'] > 0 for p in price)

    def test_calculo_ambos_metodos_api(self):
        """Testa rota /calcular/ com método 'ambos'"""
        response = client.post("/calcular/", data={
            "valor": 50000,
            "taxa": 1.5,
            "prazo": 10,
            "carencia": 0,
            "metodo": "ambos",
            "salvar": False
        })
        assert response.status_code == 200
        data = response.json()
        assert "sac" in data
        assert "price" in data
        assert len(data["sac"]) == 10
        assert len(data["price"]) == 10

    def test_somente_carencia(self):
        """Testa se o período de carência gera apenas pagamento de juros"""
        valor = 1000
        taxa = 0.05  # 5%
        carencia = 2
        amortizacoes = []

        resultado = calculo_pagamento_variavel(valor, taxa, amortizacoes, carencia)

        # Durante carência só tem juros
        assert resultado[0]['prestacao'] == 50
        assert resultado[1]['prestacao'] == 50
        assert resultado[-1]['saldo_devedor'] == 1000  # ainda não amortizou

    def test_amortizacao_total(self):
        """Testa se a dívida é zerada com amortizações suficientes"""
        valor = 1000
        taxa = 0.1  # 10%
        amortizacoes = [400, 600]  # quita em 2 parcelas

        resultado = calculo_pagamento_variavel(valor, taxa, amortizacoes)

        # Após 2 parcelas saldo devedor deve ser zero
        assert resultado[-1]['saldo_devedor'] == 0

    def test_amortizacao_incompleta(self):
        """Testa se saldo devedor é reduzido corretamente mas não zera"""
        valor = 2000
        taxa = 0.05
        amortizacoes = [500, 500]  # não quita tudo

        resultado = calculo_pagamento_variavel(valor, taxa, amortizacoes)

        # Deve restar 1000 de saldo
        assert resultado[-1]['saldo_devedor'] == 1000

    # ----------------- Testes MOCK -----------------

    @patch("main.sqlite3.connect")  # <-- MOCK do banco SQLite
    def test_database_connection_mock_erro(self, mock_connect):
        """
        Testa como a aplicação lida com falha na conexão com o banco de dados.
        """
        # Força o mock a lançar uma exceção quando tentar conectar
        mock_connect.side_effect = Exception("Falha na conexão com banco de dados")

        # Chama a rota que depende do banco
        response = client.get("/simulacoes/")

        # Verifica se a aplicação retorna status 500 (erro interno)
        assert response.status_code == 500
        
        # Verifica se a resposta contém informações de erro no formato JSON
        response_data = response.json()
        assert "detail" in response_data
        assert "erro" in response_data["detail"].lower() or "conexão" in response_data["detail"].lower()
        
        mock_connect.assert_called_once()  # ✅ Verifica se o mock foi chamado

    @patch("main.calcular_sac")
    def test_calculo_api_mock_erro(self, mock_calcular_sac):
        """Testa rota /calcular/ simulando erro interno com mock"""
        # Força o mock a lançar uma exceção
        mock_calcular_sac.side_effect = Exception("Erro simulado no cálculo")

        response = client.post("/calcular/", data={
            "valor": 10000,
            "taxa": 5,
            "prazo": 12,
            "carencia": 0,
            "metodo": "sac",
            "salvar": False
        })

        # A API deve responder erro 500
        assert response.status_code == 500
        
        # Verifica se a resposta contém informações de erro no formato JSON
        response_data = response.json()
        assert "detail" in response_data
        assert "erro" in response_data["detail"].lower() or "cálculo" in response_data["detail"].lower()

# Execução direta do teste
if __name__ == "__main__":
    print("🚀 Executando teste unitário diretamente...")
    test_instance = TestAmortizacao()
    test_instance.test_comparativo_sac_vs_price_total_pago()
    test_instance.test_sac_com_carencia()
    test_instance.test_price_valor_muito_alto()
    test_instance.test_calculo_ambos_metodos_api()
    print("🎉 Todos os testes foram executados!")
