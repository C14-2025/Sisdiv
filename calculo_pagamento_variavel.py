import carencia

from carencia import carencia


def calculo_pagamento_variavel(valor: float, taxa: float, amortizacoes: list, carencia: int = 0, temcarencia: bool = 1):
    """
    Sistema de Pagamentos Variáveis:
    - Juros do saldo devedor pagos sempre no final de cada período
    - Amortizações variam conforme lista informada

    :param valor: Valor do empréstimo
    :param taxa: Taxa de juros (ex: 0.01 para 1% ao mês)
    :param amortizacoes: Lista com os valores de amortização para cada período
    :param carencia: Número de meses de carência (paga só juros nesse período)
    """
    dados = []
    saldo_devedor = valor
    prazo = len(amortizacoes)

    # Período de carência (só juros)
    if (temcarencia):
        carencia(carencia, saldo_devedor, taxa)

    # Períodos com pagamentos variáveis
    for i, amortizacao in enumerate(amortizacoes, start=carencia + 1):
        juros = saldo_devedor * taxa
        prestacao = juros + amortizacao
        saldo_devedor -= amortizacao

        dados.append({
            "parcela": i,
            "prestacao": prestacao,
            "juros": juros,
            "amortizacao": amortizacao,
            "saldo_devedor": max(0, saldo_devedor)
        })

    return dados
