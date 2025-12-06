# calcular_sam.py

from src.calculadoras.carencia import carencia as aplicar_carencia
from typing import List, Dict, Any


def calcular_sam(valor: float,
                 taxa: float,
                 prazo: int,
                 periodo_carencia: int = 0,  # Renomeado para seguir o padrão
                 temcarencia: bool = True
                 ) -> List[Dict[str, Any]]:  # Adicionado type hint de retorno
    """
    Calcula a tabela SAM (Sistema Americano de Amortização)
    - Durante o prazo, paga-se apenas os juros.
    - Na última parcela, quita-se o principal (amortização total).

    :param valor: valor total do empréstimo
    :param taxa: taxa de juros em decimal (ex: 0.01 = 1%)
    :param prazo: número de parcelas (exclui a carência)
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
        raise ValueError("Período de carência deve ser menor que o prazo de amortização")

    parcelas = []
    saldo_devedor = valor

    # --- Aplica carência se houver ---
    if temcarencia and periodo_carencia > 0:
        parcelas += aplicar_carencia(periodo_carencia, saldo_devedor, taxa)

    # --- Monta as parcelas de Amortização (Prazo) ---
    primeira_parcela = periodo_carencia + 1
    ultima_parcela = periodo_carencia + prazo

    for i in range(1, prazo + 1):
        numero_parcela = periodo_carencia + i
        juros = round(valor * taxa, 2)  # Juros sempre sobre o valor total (principal)
        amortizacao = 0.00
        prestacao = juros
        if numero_parcela == ultima_parcela:
            amortizacao = round(valor, 2)
            prestacao = round(juros + amortizacao, 2)
            saldo_devedor_final = 0.00
        else:
            saldo_devedor_final = round(valor, 2)

        parcelas.append({
            "parcela": numero_parcela,
            "prestacao": prestacao,
            "juros": juros,
            "amortizacao": amortizacao,
            "saldo_devedor": saldo_devedor_final
        })

    return parcelas