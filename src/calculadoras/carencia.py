# carencia.py

def carencia(periodo_carencia: int, saldo_devedor: float, taxa: float):
    """
    Calcula as parcelas de carência (apenas juros) e retorna como lista de dicionários.

    :param periodo_carencia: número de meses de carência
    :param saldo_devedor: saldo devedor inicial
    :param taxa: taxa de juros em decimal (ex: 0.01 = 1%)
    :return: lista de parcelas da carência
    """

    dados = []

    for i in range(1, periodo_carencia + 1):
        juros = saldo_devedor * taxa
        prestacao = juros  # durante carência só se paga juros
        dados.append({
            "parcela": i,
            "prestacao": prestacao,
            "juros": juros,
            "amortizacao": 0,
            "saldo_devedor": saldo_devedor
        })

    # ADICIONADO: Validações importantes
    if periodo_carencia < 0:
        raise ValueError("Período de carência não pode ser negativo")
    if saldo_devedor <= 0:
        raise ValueError("Saldo devedor deve ser positivo")
    if taxa < 0:
        raise ValueError("Taxa não pode ser negativa")

    # Se não há carência, retorna lista vazia
    if periodo_carencia == 0:
        return []

    return dados
