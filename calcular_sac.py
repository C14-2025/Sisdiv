import carencia

from carencia import carencia

def calcular_sac(valor: float, taxa: float, prazo: int, carencia: int = 0, temcarencia: bool = 1):
    dados = []
    amortizacao = valor / prazo
    saldo_devedor = valor

    if(temcarencia):
        carencia(carencia, saldo_devedor, taxa)

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