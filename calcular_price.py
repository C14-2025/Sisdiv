import carencia

from carencia import carencia

def calcular_price(valor: float, taxa: float, prazo: int, carencia: int = 0, temcarencia: bool = 1):
    dados = []
    saldo_devedor = valor

    if (temcarencia):
        carencia(carencia, saldo_devedor, taxa)

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
