# calculo_pagamento_variavel.py

from carencia import carencia as aplicar_carencia

def calculo_pagamento_variavel(valor: float, taxa: float, amortizacoes: list, carencia: int = 0, temcarencia: bool = True):
    """
    Calcula pagamento variável de acordo com uma lista de amortizações.
    :param valor: valor do empréstimo
    :param taxa: taxa de juros em decimal
    :param amortizacoes: lista de amortizações por período
    :param carencia: meses de carência
    :param temcarencia: aplica carência se True
    :return: lista de parcelas com amortização, juros e saldo_devedor
    """
    if valor <= 0 or taxa < 0:
        raise ValueError("Valor e taxa devem ser positivos")

    dados = []
    saldo_devedor = valor

    # Aplica carência se houver
    if temcarencia and carencia > 0:
        dados += aplicar_carencia(carencia, saldo_devedor, taxa)

    # Monta as parcelas com base na lista de amortizações
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
