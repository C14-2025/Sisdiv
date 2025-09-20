def carencia(carencia_periodo: int, saldo_devedor: float, taxa: float):
    """
    Calcula a tabela de amortização para o período de carência.
    Retorna a lista de dados da carência e o saldo devedor atualizado.
    """
    dados = []
    # Loop para cada mês da carência
    for i in range(1, carencia_periodo + 1):
        juros = saldo_devedor * taxa
        prestacao = juros  # A prestação na carência é igual aos juros

        # O juros é somado ao saldo devedor para o próximo mês
        saldo_devedor += juros

        dados.append({
            "parcela": i,
            "prestacao": prestacao,
            "juros": juros,
            "amortizacao": 0,
            "saldo_devedor": saldo_devedor
        })

    # Retorna os dados da carência e o saldo devedor final
    return dados, saldo_devedor