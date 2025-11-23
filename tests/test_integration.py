# tests/test_integration.py
# Testes de integração do sistema de amortização

import pytest
import time
from fastapi.testclient import TestClient
from src.main import app

# =========================
# FIXTURE DO CLIENTE
# =========================
@pytest.fixture(scope="module")
def client():
    """Cria um cliente de teste da aplicação FastAPI."""
    return TestClient(app)


# =========================
# CONSTANTES DE PAYLOADS
# =========================
BASE_PAYLOAD = {
    "valor": 10000,
    "taxa": 10,
    "prazo": 6,
    "carencia": 0,
    "salvar": False,
}

PAYLOAD_PRICE = {
    "valor": 5000,
    "taxa": 8,
    "prazo": 5,
    "carencia": 0,
    "metodo": "price",
    "salvar": False,
}

PAYLOAD_SAC = {
    "valor": 8000,
    "taxa": 5,
    "prazo": 8,
    "carencia": 2,
    "metodo": "sac",
    "salvar": False,
}

# =========================
# TESTES DE INTEGRAÇÃO
# =========================

@pytest.mark.integration
def test_homepage_integration(client):
    """Verifica se a página inicial está acessível."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


@pytest.mark.integration
def test_calcular_sac_integration(client):
    payload = BASE_PAYLOAD | {"metodo": "sac"}
    response = client.post("/calcular/", data=payload)
    assert response.status_code == 200

    data = response.json()
    assert "sac" in data
    assert isinstance(data["sac"], list)
    assert len(data["sac"]) == 6


@pytest.mark.integration
def test_calcular_price_integration(client):
    response = client.post("/calcular/", data=PAYLOAD_PRICE)
    assert response.status_code == 200

    data = response.json()
    assert "price" in data
    assert isinstance(data["price"], list)
    assert len(data["price"]) == 5


@pytest.mark.integration
def test_calcular_carencia_integration(client):
    response = client.post("/calcular/", data=PAYLOAD_SAC)
    assert response.status_code == 200

    data = response.json()
    assert "sac" in data
    assert len(data["sac"]) == 10  # prazo + carência


@pytest.mark.integration
def test_calcular_metodo_invalido(client):
    payload = BASE_PAYLOAD | {"metodo": "invalido"}
    response = client.post("/calcular/", data=payload)
    assert response.status_code in [200, 400, 422]


@pytest.mark.integration
def test_calcular_campos_faltando_erro(client):
    """Teste negativo específico para validar retorno 422 quando campo obrigatório falta."""
    response = client.post("/calcular/", data={"valor": 10000, "prazo": 12})
    assert response.status_code == 422


@pytest.mark.integration
def test_calcular_integration_sem_salvar(client):
    payload = {
        "valor": 12000,
        "taxa": 6,
        "prazo": 10,
        "carencia": 0,
        "metodo": "price",
        "salvar": False,
    }
    response = client.post("/calcular/", data=payload)
    assert response.status_code == 200
    assert "price" in response.json()


@pytest.mark.integration
def test_rota_inexistente_integration(client):
    response = client.get("/nao_existe")
    assert response.status_code == 404


@pytest.mark.integration
def test_taxa_zero_integration(client):
    payload = BASE_PAYLOAD | {"taxa": 0, "metodo": "sac"}
    response = client.post("/calcular/", data=payload)

    assert response.status_code in [200, 400, 422]

    if response.status_code == 200:
        assert "sac" in response.json()


@pytest.mark.integration
def test_valor_negativo_integration(client):
    payload = BASE_PAYLOAD | {"valor": -5000, "metodo": "price"}
    response = client.post("/calcular/", data=payload)
    assert response.status_code in [200, 400, 422]


@pytest.mark.integration
def test_fluxo_completo_sac(client):
    assert client.get("/").status_code == 200

    payload = {
        "valor": 15000,
        "taxa": 10,
        "prazo": 12,
        "carencia": 0,
        "metodo": "sac",
        "salvar": False,
    }
    response = client.post("/calcular/", data=payload)
    assert response.status_code == 200
    assert "sac" in response.json()


@pytest.mark.integration
def test_performance_integration(client):
    """Valida que a API responde em menos de 2 segundos."""
    start = time.time()
    response = client.post("/calcular/", data=PAYLOAD_PRICE)
    duration = time.time() - start

    assert response.status_code == 200
    assert duration < 2.0


@pytest.mark.integration
def test_valores_altos_integration(client):
    payload = {
        "valor": 10_000_000,
        "taxa": 12,
        "prazo": 240,
        "carencia": 0,
        "metodo": "sac",
        "salvar": False,
    }
    response = client.post("/calcular/", data=payload)

    assert response.status_code == 200

    data = response.json()
    assert "sac" in data
    assert len(data["sac"]) == 240


@pytest.mark.integration
def test_prazo_curto_integration(client):
    payload = {
        "valor": 1000,
        "taxa": 10,
        "prazo": 1,
        "carencia": 0,
        "metodo": "price",
        "salvar": False
    }
    response = client.post("/calcular/", data=payload)

    assert response.status_code == 200
    assert "price" in response.json()
    assert len(response.json()["price"]) == 1
