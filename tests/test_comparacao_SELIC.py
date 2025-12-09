import pytest
import src.calculadoras.comparacao_SELIC as comp

def test_simular_comparacao_mock(monkeypatch):
    called = {"count": 0}
    def fake_get_taxa():
        called["count"] += 1
        return 7.5
    monkeypatch.setattr(comp, "get_taxa_atual_SELIC", fake_get_taxa)

    results1 = comp.simular_comparacao_SELIC('CDB', 110.0, 4, 520.0)
    '''
    expected = {
        'tipo': 'CDB',
        'percentual_base': 110.0,
        'prazo_anos': 4,
        'valor_investido': 520.0,
        'taxa_atual_SELIC': 7.5,
        'rentabilidade_total_percentual': 33.0,
        'valor_final': 691.6
    }
    '''
    # asserts
    assert called['count'] == 1
    assert isinstance(results1, dict)
    assert pytest.approx(results1['rentabilidade_total_percentual'], rel=1e-9) == 33.0
    assert pytest.approx(results1['valor_final'], rel=1e-9) == 691.6
    
    # reiniciando o contador de chamadas da função mock
    called['count'] = 0
    results2 = comp.simular_comparacao_SELIC('Poupança', 80.0, 6, 1000.0)
    '''
    expected = {
        'tipo': 'Poupança',
        'percentual_base': 80.0,
        'prazo_anos': 6,
        'valor_investido': 1000.0,
        'taxa_atual_SELIC': 7.5,
        'rentabilidade_total_percentual': 36.0,
        'valor_final': 1360.0
    }
    '''
    # asserts
    assert called['count'] == 1
    assert isinstance(results2, dict)
    assert pytest.approx(results2['rentabilidade_total_percentual'], rel=1e-9) == 36.0
    assert pytest.approx(results2['valor_final'], rel=1e-9) == 1360.0


def test_simular_comparacao_erro_em_get_taxa(monkeypatch):
    def fake_get_taxa():
        raise Exception("Erro ao buscar a taxa SELIC da API.")
    monkeypatch.setattr(comp, "get_taxa_atual_SELIC", fake_get_taxa)

    with pytest.raises(Exception) as excinfo:
        comp.simular_comparacao_SELIC(
            tipo="A",
            percentual_base=100.0,
            prazo_anos=1,
            valor_investido=100.0
        )
    assert "Erro ao buscar a taxa SELIC da API" in str(excinfo.value)

def _skip(exc):
    pytest.skip(f"API nao acessivel: {exc}")

@pytest.mark.integration
def test_get_taxa_atual_SELIC_integration():
    try:
        taxa = comp.get_taxa_atual_SELIC()
    except Exception as e:
        _skip(e)

    assert isinstance(taxa, (float, int))
    taxa = float(taxa)
    assert taxa >= 0.0, "SELIC deve ser maior que 0"
    assert taxa < 100.0, "SELIC deve ser menor que 100"


@pytest.mark.integration
def test_simular_comparacao_com_API_integration():
    percentual_map = {"CDB_TEST": 75.0, "Poupanca_TEST": 50.0}
    prazo_anos = 3
    valor_investido = 1234.56
    try:
        taxa_real = comp.get_taxa_atual_SELIC()
    except Exception as e:
        _skip(e)

    resultados = []
    try:
        for tipo, pct in percentual_map.items():
            r = comp.simular_comparacao_SELIC(
                tipo=tipo,
                percentual_base=pct,
                prazo_anos=prazo_anos,
                valor_investido=valor_investido
            )
            resultados.append(r)
    except Exception as e:
        _skip(e)

    assert isinstance(resultados, list)
    assert len(resultados) == len(percentual_map)

    for item in resultados:
        tipo = item["tipo"]
        assert tipo in percentual_map
        pct = percentual_map[tipo]
        rentabilidade_total = (float(taxa_real) * (float(pct) / 100.0)) * float(prazo_anos)
        assert pytest.approx(rentabilidade_total, rel=1e-6) == float(item["rentabilidade_total_percentual"])

        valor_final = round(valor_investido * (1 + rentabilidade_total / 100.0), 2)
        assert item["valor_final"] == valor_final
