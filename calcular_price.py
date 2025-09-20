# calcular_price.py

from carencia import carencia as aplicar_carencia

def calcular_price(valor: float, taxa: float, prazo: int, carencia: int = 0, temcarencia: bool = True):
    """
    Calcula a tabela Price (Sistema Francês de Amortização)

    :param valor: valor do empréstimo
    :param taxa: taxa de juros em decimal
    :param prazo: número de parcelas
    :param carencia: meses de carência
    :param temcarencia: aplica carência se True
    :return: lista de parcelas com amortização, juros e saldo_devedor
    """
    if valor <= 0 or prazo <= 0 or taxa < 0:
        raise ValueError("Valor, prazo e taxa devem ser positivos")

    dados = []
    saldo_devedor = valor

    # Aplica carência se houver
    if temcarencia and carencia > 0:
        dados += aplicar_carencia(carencia, saldo_devedor, taxa)

    # Calcula parcela fixa
    if taxa == 0:
        prestacao_fixa = valor / prazo
    else:
        prestacao_fixa = (valor * taxa * (1 + taxa) ** prazo) / ((1 + taxa) ** prazo - 1)

    # Monta as parcelas após carência
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
