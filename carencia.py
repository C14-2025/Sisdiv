def carencia(carencia: int, saldo_devedor: int, taxa: int):
    dados = []
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
