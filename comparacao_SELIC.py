import requests

'''
# exemplo de dicionário de entrada:
invests={
    'selic_atual': 0, # entrada
    'prazo_anos': 2, # entrada
    'valor_investido':1000, #entrada
    'investimentos': [
        # percentuais base são entrada como dict ex: {"CDB": 1.10, "LCI": 1.20}
        {"tipo": "Tesouro Selic", "percentual_base": 1},
        {"tipo": "CDB", "percentual_base": 1.10},
        {"tipo": "LCI", "percentual_base": 1.20}
    ]
}
'''

'''
percentual base é uma entrada do usuário
Taxa selic pode ser automática ou o usuário coloca manual
pode continuar retornando um dicionário, porém só com o total_investido 
'''

def get_taxa_atual_SELIC():
    try:
        # pegando o resultado da API do Banco Central
        taxa_atual_raw = requests.get('https://api.bcb.gov.br/dados/serie/bcdata.sgs.4189/dados/ultimos/1?formato=json')
        # separando a taxa atual do resultado da API
        taxa_atual = float(taxa_atual_raw.json()[0]['valor'])
        return taxa_atual
    except:
        raise Exception("Erro ao buscar a taxa SELIC da API.")

def simular_comparacao_SELIC(percentual_base: dict,
                             prazo_anos: int,
                             valor_investido: float,
                             taxa_atual_SELIC: float = None):
    
    if taxa_atual_SELIC is None:
        taxa_atual_SELIC = get_taxa_atual_SELIC()

    investimentos = []
    # calculando o rendimento para cada tipo de investimento
    for tipo, percentual in percentual_base.items():
        investimento = {'tipo':tipo, 'percentual_base': percentual}
        investimento['rentabilidade_total_percentual'] = round((taxa_atual_SELIC * percentual) * prazo_anos, 4)
        investimento['valor_final']  = round(valor_investido * (1 + investimento['rentabilidade_total_percentual'] / 100), 2)
        investimentos.append(investimento)

    return investimentos