# calculo_pagamento_variavel.py

from src.calculadoras.carencia import carencia as aplicar_carencia
from typing import List, Dict, Any


def calculo_pagamento_variavel(valor: float,
                               taxa: float,
                               amortizacoes: List[float],  # Alterado: Recebe a lista de amortizações
                               periodo_carencia: int = 0,
                               temcarencia: bool = True) -> List[Dict[str, Any]]:
    """
    Calcula pagamento variável de acordo com uma lista de amortizações.

    :param valor: valor do empréstimo
    :param taxa: taxa de juros em decimal
    :param amortizacoes: lista de amortizações por período (o tamanho define o prazo)
    :param periodo_carencia: número de meses de carência (apenas juros)
    :param temcarencia: se True, aplica a carência
    :return: lista de parcelas com amortização, juros e saldo_devedor
    """
    prazo = len(amortizacoes)  # Prazo agora é definido pelo tamanho da lista de amortizações

    if valor <= 0:
        raise ValueError("Valor do empréstimo deve ser positivo")
    if prazo <= 0:
        raise ValueError("A lista de amortizações não pode estar vazia")
    if taxa < 0:
        raise ValueError("Taxa não pode ser negativa")
    if periodo_carencia < 0:
        raise ValueError("Período de carência não pode ser negativo")
    if periodo_carencia >= prazo:
        raise ValueError("Período de carência deve ser menor que o prazo total de amortização")

    # Verificação adicional para garantir que a soma das amortizações cubra o valor
    if round(sum(amortizacoes), 2) != round(valor, 2):
        raise ValueError("A soma das amortizações deve ser igual ao valor do empréstimo")

    parcelas = []
    saldo_devedor = valor

    # --- Aplica carência se houver ---
    if temcarencia and periodo_carencia > 0:
        # A função aplicar_carencia deve retornar o saldo devedor atualizado (que permanece o mesmo)
        # e as parcelas de juros da carência.
        parcelas += aplicar_carencia(periodo_carencia, saldo_devedor, taxa)

    # --- Monta as parcelas com base na lista de amortizações ---

    # i: índice da amortização na lista (de 0 até prazo-1)
    # amortizacao_periodo: valor da amortização para o período
    for i, amortizacao_periodo in enumerate(amortizacoes):
        # O número da parcela (i + 1) deve ser ajustado para considerar o período de carência
        numero_parcela = periodo_carencia + i + 1

        # Cálculo dos juros e da prestação
        juros = round(saldo_devedor * taxa, 2)

        # A prestação é a soma dos juros calculados + a amortização do período
        prestacao = round(juros + amortizacao_periodo, 2)

        # O novo saldo devedor diminui o valor da amortização
        saldo_devedor = round(saldo_devedor - amortizacao_periodo, 2)

        parcelas.append({
            "parcela": numero_parcela,
            "prestacao": prestacao,
            "juros": juros,
            "amortizacao": amortizacao_periodo,  # Usa a amortização da lista
            "saldo_devedor": max(0, saldo_devedor)  # Garante que não é negativo no final
        })

    return parcelas