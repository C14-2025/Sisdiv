# calculos.py

def calcular_sac(valor: float, taxa: float, prazo: int, carencia: int = 0):
    dados = []
    amortizacao = valor / prazo
    saldo_devedor = valor

    for i in range(1, carencia + 1):
        juros = saldo_devedor * taxa
        prestacao = juros
        dados.append({
            "parcela": i,
            "prestacao": prestacao,
            "juros": juros,
            "amortizacao": 0,
            "saldo_devedor": saldo_devedor
        })

    for i in range(carencia + 1, carencia + prazo + 1):
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

def calcular_price(valor: float, taxa: float, prazo: int, carencia: int = 0):
    dados = []
    saldo_devedor = valor

    for i in range(1, carencia + 1):
        juros = saldo_devedor * taxa
        prestacao = juros
        dados.append({
            "parcela": i,
            "prestacao": prestacao,
            "juros": juros,
            "amortizacao": 0,
            "saldo_devedor": saldo_devedor
        })

    if prazo > 0:
        prestacao_fixa = (valor * taxa * (1 + taxa) ** prazo) / ((1 + taxa) ** prazo - 1)
    else:
        prestacao_fixa = 0

    for i in range(carencia + 1, carencia + prazo + 1):
        juros = saldo_devedor * taxa
        amortizacao = prestacao_fixa - juros
        saldo_devedor -= amortizacao

        dados.append({
            "parcela": i,
            "prestacao": prestacao_fixa,
            "juros": juros,
            "amortizacao": amortizacao,
            "saldo_devedor": max(0, saldo_devedor)
        })

    return dados


def calcular_pagamentos_variaveis(valor: float, taxa: float, amortizacoes: list, carencia: int = 0):
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
    for i in range(1, carencia + 1):
        juros = saldo_devedor * taxa
        prestacao = juros
        dados.append({
            "parcela": i,
            "prestacao": prestacao,
            "juros": juros,
            "amortizacao": 0,
            "saldo_devedor": saldo_devedor
        })

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
