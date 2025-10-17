import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Adiciona o diretório raiz para permitir a importação dos módulos
# Apenas para garantir que o teste funcione, mas em projetos reais use a estrutura do poetry/pip
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.calculadoras.calcular_price import calcular_price

class TestAmortizacaoPriceComMock:
    """Testes unitários para o sistema de amortização PRICE com mocks."""

    # Usa um mock para a função 'carencia' dentro do módulo 'calcular_price'
    @patch('calcular_price.aplicar_carencia')
    def test_calcular_price_com_carencia_mockada(self, mock_aplicar_carencia: MagicMock):
        """
        Testa o cálculo da tabela PRICE com carência, simulando a função de carência
        para isolar o teste da lógica de amortização.
        """
        # 1. ARRANGE - Configuração do Mock e Dados de Entrada
        valor_emprestimo = 10000.0
        taxa_juros = 0.005
        prazo_amortizacao = 10
        periodo_carencia = 2

        # Define o saldo devedor após a carência, que será o ponto de partida para o cálculo PRICE.
        saldo_devedor_final_carencia = 10100.25

        # Cria os dados simulados que o mock irá retornar.
        # Estes dados simulam as duas primeiras parcelas da carência.
        dados_mockados_carencia = [
            {"parcela": 1, "prestacao": pytest.approx(50.0), "juros": pytest.approx(50.0), "amortizacao": 0.0,
             "saldo_devedor": 10050.0},
            {"parcela": 2, "prestacao": pytest.approx(50.25), "juros": pytest.approx(50.25), "amortizacao": 0.0,
             "saldo_devedor": saldo_devedor_final_carencia}
        ]

        # A nova versão da função de carencia retorna apenas a lista de parcelas.
        # Por isso, o retorno do mock precisa ser ajustado.
        mock_aplicar_carencia.return_value = dados_mockados_carencia

        # 2. ACT - Execução da Função a Ser Testada
        # A função calcular_price será executada e, internamente, chamará o mock.
        resultado_final = calcular_price(
            valor=valor_emprestimo,
            taxa=taxa_juros,
            prazo=prazo_amortizacao,
            carencia=periodo_carencia,
            temcarencia=True
        )

        # 3. ASSERT - Verificação do Resultado

        # O mock deve ter sido chamado com os parâmetros corretos.
        mock_aplicar_carencia.assert_called_once_with(periodo_carencia, valor_emprestimo, taxa_juros)

        # O resultado final deve conter o total de parcelas.
        assert len(resultado_final) == periodo_carencia + prazo_amortizacao

        # Verifica se as parcelas de carência no resultado correspondem aos dados mockados.
        assert resultado_final[:periodo_carencia] == dados_mockados_carencia

        # Valida se o cálculo da prestação fixa está correto, usando o saldo final da carência mockada.
        prestacao_fixa_esperada = (saldo_devedor_final_carencia * taxa_juros * (
                    1 + taxa_juros) ** prazo_amortizacao) / ((1 + taxa_juros) ** prazo_amortizacao - 1)

        # A prestação da primeira parcela de amortização deve ser a calculada acima.
        assert resultado_final[periodo_carencia]["prestacao"] == pytest.approx(prestacao_fixa_esperada)

        # O juros da primeira parcela de amortização deve ser baseado no saldo final da carência mockada.
        juros_primeira_amortizacao = resultado_final[periodo_carencia]["juros"]
        assert juros_primeira_amortizacao == pytest.approx(saldo_devedor_final_carencia * taxa_juros)

        # O saldo devedor da primeira parcela de amortização deve ser o saldo final da carência menos a amortização.
        amortizacao_primeira_parcela = prestacao_fixa_esperada - juros_primeira_amortizacao
        saldo_devedor_esperado_primeira_parcela = saldo_devedor_final_carencia - amortizacao_primeira_parcela

        assert resultado_final[periodo_carencia]["saldo_devedor"] == pytest.approx(
            saldo_devedor_esperado_primeira_parcela)