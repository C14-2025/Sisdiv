import pytest
import sys
import os
from unittest.mock import patch

# Adiciona o diretório raiz ao path para importar o módulo calculos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from calcular_sac import calcular_sac
from calcular_price import calcular_price
from calculo_pagamento_variavel import calculo_pagamento_variavel
from fastapi.testclient import TestClient
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

client = TestClient(app)

def formatar_brl(valor):
    """Formata valores no padrão brasileiro R$ 1.000,00"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

class TestAmortizacao:
    """Testes unitários para o sistema de amortização"""

    # Rotas da API
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
        """Testa a rota de cálculo e verifica se retorna JSON válido"""
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

    # Testes de cálculos
    def test_comparativo_sac_vs_price_total_pago(self):
        """Comparação SAC vs Price: SAC deve ser mais vantajoso"""
        valor = 100000
        taxa = 0.01
        prazo = 12

        sac = calcular_sac(valor, taxa, prazo)
        price = calcular_price(valor, taxa, prazo)

        total_sac = sum(p['prestacao'] for p in sac)
        total_price = sum(p['prestacao'] for p in price)

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

    # ---  testes ---
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

        # Durante carência só tem juros (50 por mês)
        self.assertEqual(resultado[0]['prestacao'], 50)
        self.assertEqual(resultado[1]['prestacao'], 50)
        self.assertEqual(resultado[-1]['saldo_devedor'], 1000)  # ainda não amortizou

    def test_amortizacao_total(self):
        """Testa se a dívida é zerada com amortizações suficientes"""
        valor = 1000
        taxa = 0.1  # 10%
        amortizacoes = [400, 600]  # quita em 2 parcelas

        resultado = calculo_pagamento_variavel(valor, taxa, amortizacoes)

        # Após 2 parcelas saldo devedor deve ser zero
        self.assertEqual(resultado[-1]['saldo_devedor'], 0)

    def test_amortizacao_incompleta(self):
        """Testa se saldo devedor é reduzido corretamente mas não zera"""
        valor = 2000
        taxa = 0.05
        amortizacoes = [500, 500]  # não quita tudo

        resultado = calculo_pagamento_variavel(valor, taxa, amortizacoes)

        # Deve restar 1000 de saldo
        self.assertEqual(resultado[-1]['saldo_devedor'], 1000)

    # --- NOVO TESTE COM MOCK ---
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
        assert "erro" in response.text.lower() or "error" in response.text.lower()


# Execução direta do teste
if __name__ == "__main__":
    print("🚀 Executando teste unitário diretamente...")
    test_instance = TestAmortizacao()
    test_instance.test_comparativo_sac_vs_price_total_pago()
    test_instance.test_sac_com_carencia()
    test_instance.test_price_valor_muito_alto()
    test_instance.test_calculo_ambos_metodos_api()
    print("🎉 Todos os testes foram executados!")
