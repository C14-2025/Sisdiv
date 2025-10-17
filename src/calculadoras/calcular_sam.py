# calcular_sam.py

from src.calculadoras.carencia import carencia as aplicar_carencia

def calcular_sam(valor: float, taxa: float, prazo: int, carencia: int = 0, temcarencia: bool = True):
    """
    Sistema Americano de Amortização (SAM)
    - Durante o prazo, paga-se apenas os juros.
    - Na última parcela, quita-se o principal (amortização total).
    """
    dados = []
    saldo_devedor = valor

    # Aplica carência se houver e atualiza o saldo devedor
    if temcarencia and carencia > 0:
        carencia_data = aplicar_carencia(carencia, saldo_devedor, taxa)
        dados += carencia_data

    for i in range(1, prazo + 1):
        juros = valor * taxa
        amortizacao = 0
        prestacao = juros

        # Na última parcela, amortiza todo o principal
        if i == prazo:
            amortizacao = valor
            prestacao += valor
            saldo_devedor = 0
        else:
            saldo_devedor = valor  # permanece o mesmo até o final

        dados.append({
            "parcela": i,
            "prestacao": prestacao,
            "juros": juros,
            "amortizacao": amortizacao,
            "saldo_devedor": saldo_devedor
        })

    return dados
