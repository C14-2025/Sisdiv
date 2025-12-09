import requests

def get_taxa_atual_SELIC():
    try:
        # pegando o resultado da API do Banco Central
        taxa_atual_raw = requests.get('https://api.bcb.gov.br/dados/serie/bcdata.sgs.4189/dados/ultimos/1?formato=json')
        # separando a taxa atual do resultado da API
        taxa_atual = float(taxa_atual_raw.json()[0]['valor'].replace(',', '.'))
        return taxa_atual
    except Exception as e:
        raise Exception("Erro ao buscar a taxa SELIC da API")

def simular_comparacao_SELIC(tipo: str,
                             percentual_base: float,
                             prazo_anos: int,
                             valor_investido: float): # type: ignore
    
    
    taxa_atual_SELIC = get_taxa_atual_SELIC()

    # Calculando rendimento
    investimentoResult = {}
    investimentoResult['tipo'] = tipo
    investimentoResult['percentual_base'] = percentual_base
    investimentoResult['prazo_anos'] = prazo_anos
    investimentoResult['valor_investido'] = valor_investido
    investimentoResult['taxa_atual_SELIC'] = taxa_atual_SELIC
    investimentoResult['rentabilidade_total_percentual'] = round((taxa_atual_SELIC * (percentual_base / 100)) * prazo_anos, 4)
    investimentoResult['valor_final'] = round(valor_investido * (1 + investimentoResult['rentabilidade_total_percentual'] / 100), 2)

    return investimentoResult
