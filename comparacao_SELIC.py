import requests

'''
# exemplo de dicionário de entrada:
invests={
    'selic_atual': 0,
    'prazo_anos': 2,
    'valor_investido':1000,
    'investimentos': [
        {"tipo": "Tesouro Selic", "percentual_base": 1},
        {"tipo": "CDB", "percentual_base": 1.10},
        {"tipo": "LCI", "percentual_base": 1.20}
    ]
}
'''

def simular_comparacao_SELIC(investimentos: dict):
    try:
        # pegando o resultado da API do Banco Central
        taxa_atual_raw = requests.get('https://api.bcb.gov.br/dados/serie/bcdata.sgs.4189/dados/ultimos/1?formato=json')
        # separando a taxa atual do resultado da API
        taxa_atual = float(taxa_atual_raw.json()[0]['valor'])
    except:
        raise Exception("Erro ao buscar a taxa SELIC da API.")
    
    # calculando o rendimento para cada tipo de investimento
    for i in investimentos['investimentos']:
        i['rentabilidade_total_percentual'] = round((taxa_atual * i['percentual_base']) * investimentos['prazo_anos'], 4)
        i['valor_final'] = round(investimentos['valor_investido'] * (1 + i['rentabilidade_total_percentual'] / 100), 2)
    
    investimentos['selic_atual'] = taxa_atual

    return investimentos