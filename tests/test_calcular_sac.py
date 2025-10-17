import pytest
from unittest.mock import patch

from src.calculadoras.calcular_sac import calcular_sac

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


# 🔹 Teste Sac sem periodo de carencia
def test_calcular_sac_sem_carencia():
    """Verifica se o cálculo SAC funciona corretamente quando não há período de carência."""
    valor = 1200
    taxa = 0.05
    prazo = 3
    resultado = calcular_sac(valor, taxa, prazo)

    # Garante que há 3 parcelas no resultado
    assert len(resultado) == prazo
    # O saldo devedor final deve ser zero
    assert resultado[-1]["saldo_devedor"] == 0
