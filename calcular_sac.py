from carencia import carencia as aplicar_carencia  # renomeia a função importada para evitar conflito

def calcular_sac(valor: float, taxa: float, prazo: int, periodo_carencia: int = 0, temcarencia: bool = True):
    """
    Calcula a tabela SAC (Sistema de Amortização Constante)

    :param valor: valor total do empréstimo
    :param taxa: taxa de juros em decimal (ex: 0.01 = 1%)
    :param prazo: número de parcelas
    :param periodo_carencia: número de meses de carência (apenas juros)
    :param temcarencia: se True, aplica a carência
    :return: lista de dicionários com parcelas
    """
    if valor <= 0 or prazo <= 0 or taxa < 0:
        raise ValueError("Valor, prazo e taxa devem ser positivos")

    dados = []
    amortizacao = valor / prazo
    saldo_devedor = valor

    # Aplica carência se houver
    if temcarencia and periodo_carencia > 0:
        dados += aplicar_carencia(periodo_carencia, saldo_devedor, taxa)

    # Monta as parcelas após carência
    for i in range(periodo_carencia + 1, periodo_carencia + prazo + 1):
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
