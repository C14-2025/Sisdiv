import pytest
from unittest.mock import patch

from calcular_sac import calcular_sac

def test_calcular_sac_com_carencia_mock():
    valor = 1000
    taxa = 0.05
    prazo = 3
    periodo_carencia = 2

    carencia_resultado = [
        {"parcela": 1, "prestacao": 50, "juros": 50, "amortizacao": 0, "saldo_devedor": 1000},
        {"parcela": 2, "prestacao": 50, "juros": 50, "amortizacao": 0, "saldo_devedor": 1000},
    ]

    with patch("calcular_sac.aplicar_carencia", return_value=carencia_resultado) as mock_carencia:
        resultado = calcular_sac(valor, taxa, prazo, periodo_carencia, temcarencia=True)

        # Assert
        mock_carencia.assert_called_once_with(periodo_carencia, valor, taxa)
        # resultado começa com carencia_resultado simulado
        assert resultado[:2] == carencia_resultado
        # restante é o cálculo normal do SAC
        assert len(resultado) == periodo_carencia + prazo