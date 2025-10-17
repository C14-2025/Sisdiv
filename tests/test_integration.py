from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_homepage_integration():
    """Verifica se a página inicial carrega corretamente"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_calcular_integration():
    """Testa rota /calcular/ com dados reais"""
    response = client.post("/calcular/", data={
        "valor": 10000,
        "taxa": 5,
        "prazo": 12,
        "carencia": 0,
        "metodo": "sac",
        "salvar": False
    })
    assert response.status_code == 200
    data = response.json()
    assert "sac" in data
    assert isinstance(data["sac"], list)
