# tests/test_integration.py
# Descrição: Testes de integração do sistema de amortização

import pytest
import time
from fastapi.testclient import TestClient
from src.main import app


# ========== FIXTURE NECESSÁRIA ==========
@pytest.fixture(scope="module")
def client():
    """Cria um cliente de teste da aplicação FastAPI"""
    return TestClient(app)


# ========== TESTES DE INTEGRAÇÃO ==========

# Rota principal
def test_homepage_integration(client):
    """Verifica se a página inicial responde corretamente"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


# Cálculo SAC
def test_calcular_sac_integration(client):
    response = client.post("/calcular/", data={
        "valor": 10000, "taxa": 10, "prazo": 6,
        "carencia": 0, "metodo": "sac", "salvar": False
    })
    assert response.status_code == 200
    data = response.json()
    assert "sac" in data
    assert len(data["sac"]) == 6


# Cálculo PRICE 
def test_calcular_price_integration(client):
    response = client.post("/calcular/", data={
        "valor": 5000, "taxa": 8, "prazo": 5,
        "carencia": 0, "metodo": "price", "salvar": False
    })
    assert response.status_code == 200
    data = response.json()
    assert "price" in data
    assert len(data["price"]) == 5


# Cálculo com carência
def test_calcular_carencia_integration(client):
    response = client.post("/calcular/", data={
        "valor": 8000, "taxa": 5, "prazo": 8,
        "carencia": 2, "metodo": "sac", "salvar": False
    })
    assert response.status_code == 200
    data = response.json()
    assert "sac" in data
    assert len(data["sac"]) == 10


# Método inválido
def test_calcular_metodo_invalido(client):
    response = client.post("/calcular/", data={
        "valor": 10000, "taxa": 10, "prazo": 12,
        "carencia": 0, "metodo": "invalido", "salvar": False
    })
    assert response.status_code in [400, 422]


# Campos ausentes
def test_calcular_campos_faltando(client):
    response = client.post("/calcular/", data={
        "valor": 10000,
        "prazo": 12,
        "metodo": "sac"
    })
    assert response.status_code in [400, 422]


# Simulação de salvar no banco
def test_calcular_integration_salvar(client):
    response = client.post("/calcular/", data={
        "valor": 12000, "taxa": 6, "prazo": 10,
        "carencia": 0, "metodo": "price", "salvar": True
    })
    assert response.status_code == 200
    data = response.json()
    assert "price" in data


# Rota inexistente
def test_rota_inexistente_integration(client):
    response = client.get("/nao_existe")
    assert response.status_code == 404


# Taxa zero
def test_taxa_zero_integration(client):
    response = client.post("/calcular/", data={
        "valor": 10000, "taxa": 0, "prazo": 6,
        "carencia": 0, "metodo": "sac", "salvar": False
    })
    assert response.status_code == 200
    data = response.json()
    assert "sac" in data


# Valor negativo
def test_valor_negativo_integration(client):
    response = client.post("/calcular/", data={
        "valor": -5000, "taxa": 10, "prazo": 6,
        "carencia": 0, "metodo": "price", "salvar": False
    })
    assert response.status_code in [400, 422]


# Fluxo completo SAC: acessar → calcular → salvar
def test_fluxo_completo_sac(client):
    r1 = client.get("/")
    assert r1.status_code == 200

    r2 = client.post("/calcular/", data={
        "valor": 15000, "taxa": 10, "prazo": 12,
        "carencia": 0, "metodo": "sac", "salvar": True
    })
    assert r2.status_code == 200
    data = r2.json()
    assert "sac" in data

    # Verifica se os resultados são acessíveis (se houver rota)
    r3 = client.get("/resultados/")
    assert r3.status_code in [200, 404]  # depende da implementação


# Performance: tempo de resposta
def test_performance_integration(client):
    start = time.time()
    response = client.post("/calcular/", data={
        "valor": 10000, "taxa": 8, "prazo": 6,
        "carencia": 0, "metodo": "price"
    })
    end = time.time()
    assert response.status_code == 200
    assert (end - start) < 1.0  # deve responder em até 1s


# Stress: valores altos
def test_valores_altos_integration(client):
    response = client.post("/calcular/", data={
        "valor": 10_000_000, "taxa": 12, "prazo": 240,
        "carencia": 0, "metodo": "sac", "salvar": False
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["sac"]) == 240


# Prazo muito curto
def test_prazo_curto_integration(client):
    response = client.post("/calcular/", data={
        "valor": 1000, "taxa": 10, "prazo": 1,
        "carencia": 0, "metodo": "price", "salvar": False
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["price"]) == 1