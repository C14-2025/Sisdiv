import requests

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
                             taxa_atual_SELIC: float = None): # type: ignore
    
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
