import pytest
import src.calculadoras.comparacao_SELIC

def test_simular_comparacao_with_taxa_provided():
    percentual_base = {"CDB": 0.8, "Poupanca": 0.5}
    prazo_anos = 2
    valor_investido = 1000.0
    taxa_atual_SELIC = 10.0

    resultados = src.calculadoras.comparacao_SELIC.simular_comparacao_SELIC(
        percentual_base=percentual_base,
        prazo_anos=prazo_anos,
        valor_investido=valor_investido,
        taxa_atual_SELIC=taxa_atual_SELIC
    )
    assert isinstance(resultados, list)
    assert len(resultados) == 2

    cdb = next(x for x in resultados if x["tipo"] == "CDB")
    assert cdb["rentabilidade_total_percentual"] == 16.0
    assert cdb["valor_final"] == 1160.00

    poup = next(x for x in resultados if x["tipo"] == "Poupanca")
    assert poup["rentabilidade_total_percentual"] == 10.0
    assert poup["valor_final"] == 1100.00


def test_simular_comparacao_usa_get_taxa_qdo_vazio(monkeypatch):
    called = {"count": 0}
    def fake_get_taxa():
        called["count"] += 1
        return 7.5

    monkeypatch.setattr(src.calculadoras.comparacao_SELIC, "get_taxa_atual_SELIC", fake_get_taxa)
    percentual_base = {"FundoX": 1.0}
    resultados = src.calculadoras.comparacao_SELIC.simular_comparacao_SELIC(
        percentual_base=percentual_base,
        prazo_anos=1,
        valor_investido=200.0,
        taxa_atual_SELIC=None # type: ignore
    )

    assert called["count"] == 1
    assert len(resultados) == 1
    r = resultados[0]
    assert r["rentabilidade_total_percentual"] == 7.5
    assert r["valor_final"] == 215.00

def test_simular_comparacao_erro_em_get_taxa(monkeypatch):
    def fake_get_taxa():
        raise Exception("Erro ao buscar a taxa SELIC da API.")

    monkeypatch.setattr(src.calculadoras.comparacao_SELIC, "get_taxa_atual_SELIC", fake_get_taxa)

    with pytest.raises(Exception) as excinfo:
        src.calculadoras.comparacao_SELIC.simular_comparacao_SELIC(
            percentual_base={"A": 1.0},
            prazo_anos=1,
            valor_investido=100.0,
            taxa_atual_SELIC=None   # type: ignore
        )
    assert "Erro ao buscar taxa SELIC" in str(excinfo.value)



def _skip(exc):
    pytest.skip(f"API nao acessivel: {exc}")

@pytest.mark.integration
def test_get_taxa_atual_SELIC_integration():
    try:
        taxa = src.calculadoras.comparacao_SELIC.get_taxa_atual_SELIC()
    except Exception as e:
        _skip(e)

    assert isinstance(taxa, float) or isinstance(taxa, int)
    taxa = float(taxa)
    assert taxa >= 0.0, "SELIC deve ser maior que 0"
    assert taxa < 100.0, "SELIC deve ser menor que 100"

@pytest.mark.integration
def test_simular_comparacao_com_API_integration():
    percentual_base = {"CDB_TEST": 0.75, "Poupanca_TEST": 0.5}
    prazo_anos = 3
    valor_investido = 1234.56

    try:
        taxa_real = src.calculadoras.comparacao_SELIC.get_taxa_atual_SELIC()
    except Exception as e:
        _skip(e)

    try:
        resultados = src.calculadoras.comparacao_SELIC.simular_comparacao_SELIC(
            percentual_base=percentual_base,
            prazo_anos=prazo_anos,
            valor_investido=valor_investido,
            taxa_atual_SELIC=None  # type: ignore
        )
    except Exception as e:
        _skip(e)

    assert isinstance(resultados, list)
    assert len(resultados) == len(percentual_base)

    for item in resultados:
        tipo = item["tipo"]
        assert tipo in percentual_base
        pct = percentual_base[tipo]
        rentabilidade_total = (float(taxa_real) * float(pct)) * float(prazo_anos)
        assert pytest.approx(rentabilidade_total, rel=1e-6) == float(item["rentabilidade_total_percentual"])
        
        valor_final = round(valor_investido * (1 + rentabilidade_total / 100.0), 2)
        assert item["valor_final"] == valor_final