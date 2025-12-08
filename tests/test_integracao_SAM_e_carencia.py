import pytest
from src.calculadoras.calcular_sam import calcular_sam


class TestIntegracaoSamCarencia:

    def test_fluxo_completo_sam_com_carencia(self):
        valor = 10000.00
        taxa = 0.02  # 2%
        prazo_amortizacao = 4
        periodo_carencia = 3

        resultado = calcular_sam(
            valor=valor,
            taxa=taxa,
            prazo=prazo_amortizacao,
            periodo_carencia=periodo_carencia,
            temcarencia=True
        )

        assert len(resultado) == prazo_amortizacao + periodo_carencia

        valor_juros_esperado = 200.00  # 10.000 * 0.02

        for i in range(periodo_carencia):
            parcela = resultado[i]
            assert parcela["parcela"] == i + 1
            assert parcela["prestacao"] == pytest.approx(valor_juros_esperado)
            assert parcela["juros"] == pytest.approx(valor_juros_esperado)
            assert parcela["amortizacao"] == 0.00
            assert parcela["saldo_devedor"] == valor

        for i in range(periodo_carencia, len(resultado) - 1):
            parcela = resultado[i]
            assert parcela["parcela"] == i + 1
            assert parcela["prestacao"] == pytest.approx(valor_juros_esperado)
            assert parcela["amortizacao"] == 0.00
            assert parcela["saldo_devedor"] == valor

        ultima_parcela = resultado[-1]
        assert ultima_parcela["parcela"] == 7
        assert ultima_parcela["prestacao"] == pytest.approx(valor_juros_esperado + valor)
        assert ultima_parcela["amortizacao"] == pytest.approx(valor)
        assert ultima_parcela["saldo_devedor"] == 0.00
