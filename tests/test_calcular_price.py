import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Adiciona o diretório raiz ao path para importar o módulo calculos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calcular_price import calcular_price


class TestAmortizacaodoPrice:
    """Testes unitários para o sistema de amortização"""

    # ... (Seus outros testes, como o test_calculo_api_mock_erro)

    @patch("calcular_price.carencia")
    def test_calcular_price_com_carencia_mockada(self, mock_carencia):
        """
        Testa a função calcular_price garantindo que ela processa
        corretamente os dados retornados pela função de carência mockada.
        """
        # 1. Configurar o mock:
        # A função 'carencia' deve retornar uma tupla: (dados da carencia, novo_saldo_devedor)
        dados_mockados_carencia = [
            {"parcela": 1, "prestacao": 50.0, "juros": 50.0, "amortizacao": 0, "saldo_devedor": 10050.0},
            {"parcela": 2, "prestacao": 50.25, "juros": 50.25, "amortizacao": 0, "saldo_devedor": 10100.25},
            {"parcela": 3, "prestacao": 50.50, "juros": 50.50, "amortizacao": 0, "saldo_devedor": 10150.75}
        ]
        novo_saldo_mockado = 10150.75

        mock_carencia.return_value = (dados_mockados_carencia, novo_saldo_mockado)

        # 2. Chamar a função a ser testada:
        # Note que passamos `temcarencia=True` e `carencia_periodo=3`
        resultado = calcular_price(valor=10000, taxa=0.005, prazo=12, carencia_periodo=3, temcarencia=True)

        # 3. Verificar o comportamento e o resultado:

        # Verifique se a função 'carencia' foi chamada exatamente uma vez,
        # com os argumentos corretos.
        mock_carencia.assert_called_once_with(3, 10000, 0.005)

        # O resultado final deve ter o número total de parcelas (carencia + prazo)
        assert len(resultado) == 15

        # As 3 primeiras entradas do resultado devem ser os dados mockados da carencia.
        assert resultado[:3] == dados_mockados_carencia

        # A primeira parcela de amortização (parcela 4) deve usar o novo saldo devedor.
        # Vamos calcular o juros esperado para a 4ª parcela (que é a 1ª de amortização)
        juros_esperado_primeira_amortizacao = novo_saldo_mockado * 0.005
        assert resultado[3]["parcela"] == 4
        assert pytest.approx(resultado[3]["juros"]) == juros_esperado_primeira_amortizacao