# calcular_price.py

from src.calculadoras.carencia import carencia as aplicar_carencia

def calcular_price(valor: float, taxa: float, prazo: int, carencia: int = 0, temcarencia: bool = True):
    # ... (código existente)

    dados = []
    saldo_devedor = valor

    # Aplica carência se houver e atualiza o saldo devedor
    if temcarencia and carencia > 0:
        carencia_data = aplicar_carencia(carencia, saldo_devedor, taxa)
        dados += carencia_data
        # O saldo devedor da última parcela da carência se torna o novo saldo inicial
        # para o cálculo da tabela Price.
        saldo_devedor = carencia_data[-1]["saldo_devedor"]

    # Calcula parcela fixa com o saldo devedor ATUALIZADO
    if taxa == 0:
        prestacao_fixa = saldo_devedor / prazo
    else:
        # AQUI ESTÁ A CORREÇÃO: Usa 'saldo_devedor' em vez de 'valor'
        prestacao_fixa = (saldo_devedor * taxa * (1 + taxa) ** prazo) / ((1 + taxa) ** prazo - 1)

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