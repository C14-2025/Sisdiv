# Importa apenas a função 'carencia' do módulo 'carencia'
from carencia import carencia


def calcular_price(valor: float, taxa: float, prazo: int, carencia_periodo: int = 0, temcarencia: bool = True):
    """
    Calcula a tabela de amortização pelo método PRICE.

    Args:
        valor (float): O valor inicial do empréstimo.
        taxa (float): A taxa de juros mensal.
        prazo (int): O número de meses do financiamento (excluindo a carência).
        carencia_periodo (int): O período de carência em meses.
        temcarencia (bool): Se deve ou não considerar a carência.

    Returns:
        list: Uma lista de dicionários com a tabela de amortização.
    """
    dados = []
    saldo_devedor = valor

    if temcarencia and carencia_periodo > 0:
        # Chama a função de carência e captura os dados e o novo saldo devedor
        dados_carencia, novo_saldo = carencia(carencia_periodo, saldo_devedor, taxa)

        # Adiciona os dados da carência à lista principal
        dados.extend(dados_carencia)

        # Atualiza o saldo devedor com o valor acumulado durante a carência
        saldo_devedor = novo_saldo

    if prazo > 0:
        # A prestação fixa deve ser calculada com base no novo saldo devedor
        # e no prazo do financiamento
        prestacao_fixa = (saldo_devedor * taxa * (1 + taxa) ** prazo) / ((1 + taxa) ** prazo - 1)
    else:
        prestacao_fixa = 0

    # O loop principal começa após o período de carência
    for i in range(carencia_periodo + 1, carencia_periodo + prazo + 1):
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