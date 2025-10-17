import pytest
from unittest.mock import patch
from src.calculadoras.calcular_sam import calcular_sam


def test_calcular_sam_com_carencia_mock():
    """
    Testa se o cálculo do SAM aplica corretamente a carência,
    simulando a função aplicar_carencia com mock.
    """
    valor = 1000
    taxa = 0.05
    prazo = 3
    periodo_carencia = 2

    # Resultado simulado da função aplicar_carencia
    carencia_resultado = [
        {"parcela": 1, "prestacao": 50, "juros": 50, "amortizacao": 0, "saldo_devedor": 1000},
        {"parcela": 2, "prestacao": 50, "juros": 50, "amortizacao": 0, "saldo_devedor": 1000},
    ]

    # Simula a função aplicar_carencia dentro do módulo calcular_sam
    with patch("calcular_sam.aplicar_carencia", return_value=carencia_resultado) as mock_carencia:
        resultado = calcular_sam(valor, taxa, prazo, periodo_carencia, temcarencia=True)

        # Verifica se a função foi chamada corretamente
        mock_carencia.assert_called_once_with(periodo_carencia, valor, taxa)

        # As duas primeiras parcelas devem vir do mock
        assert resultado[:2] == carencia_resultado

        # O número total de parcelas deve incluir carência + prazo
        assert len(resultado) == periodo_carencia + prazo

        # Após a carência, o sistema deve pagar apenas juros, exceto na última
        for parcela in resultado[periodo_carencia:-1]:
            assert parcela["juros"] == pytest.approx(valor * taxa)
            assert parcela["amortizacao"] == 0
            assert parcela["saldo_devedor"] == valor

        # Última parcela: amortiza o principal
        ultima = resultado[-1]
        assert ultima["prestacao"] == pytest.approx(valor * taxa + valor)
        assert ultima["amortizacao"] == valor
        assert ultima["saldo_devedor"] == 0


def test_calcular_sam_sem_carencia_nao_chama_mock():
    """
    Testa se o cálculo do SAM funciona normalmente sem carência
    e se a função aplicar_carencia não é chamada.
    """
    valor = 1000
    taxa = 0.05
    prazo = 3
    periodo_carencia = 2

    with patch("calcular_sam.aplicar_carencia") as mock_carencia:
        resultado = calcular_sam(valor, taxa, prazo, periodo_carencia, temcarencia=False)

        # Garante que a função de carência não foi chamada
        mock_carencia.assert_not_called()

        # Deve ter apenas as 3 parcelas do prazo
        assert len(resultado) == prazo

        # As duas primeiras parcelas: apenas juros
        for parcela in resultado[:-1]:
            assert parcela["prestacao"] == pytest.approx(valor * taxa)
            assert parcela["juros"] == pytest.approx(valor * taxa)
            assert parcela["amortizacao"] == 0
            assert parcela["saldo_devedor"] == valor

        # Última parcela: quita o valor principal
        ultima = resultado[-1]
        assert ultima["prestacao"] == pytest.approx(valor * taxa + valor)
        assert ultima["amortizacao"] == valor
        assert ultima["saldo_devedor"] == 0
