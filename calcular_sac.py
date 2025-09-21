from carencia import carencia as aplicar_carencia  # renomeia a função importada para evitar conflito
from typing import List, Dict, Any

def calcular_sac(valor: float, 
                 taxa: float, 
                 prazo: int, 
                 periodo_carencia: int = 0, 
                 temcarencia: bool = True
                 )-> List[Dict[str, Any]]:
    """
    Calcula a tabela SAC (Sistema de Amortização Constante)

    :param valor: valor total do empréstimo
    :param taxa: taxa de juros em decimal (ex: 0.01 = 1%)
    :param prazo: número de parcelas
    :param periodo_carencia: número de meses de carência (apenas juros)
    :param temcarencia: se True, aplica a carência
    :return: lista de dicionários com parcelas
    """
    if valor <= 0:
        raise ValueError("Valor do empréstimo deve ser positivo")
    if prazo <= 0:
        raise ValueError("Prazo deve ser positivo")
    if taxa < 0:
        raise ValueError("Taxa não pode ser negativa")
    if periodo_carencia < 0:
        raise ValueError("Período de carência não pode ser negativo")
    if periodo_carencia >= prazo:
        raise ValueError("Período de carência deve ser menor que o prazo total")

    parcelas = []
    amortizacao = round(valor / prazo, 2)
    saldo_devedor = valor

    # Aplica carência se houver
    if temcarencia and periodo_carencia > 0:
        parcelas += aplicar_carencia(periodo_carencia, saldo_devedor, taxa)

    # Monta as parcelas após carência
    for i in range(periodo_carencia + 1, periodo_carencia + prazo + 1):
        juros = round(saldo_devedor * taxa, 2)
        prestacao = round(juros + amortizacao, 2)
        saldo_devedor = round(saldo_devedor - amortizacao, 2)

        parcelas.append({
            "parcela": i,
            "prestacao": prestacao,
            "juros": juros,
            "amortizacao": amortizacao,
            "saldo_devedor": max(0, saldo_devedor)
        })

    return parcelas