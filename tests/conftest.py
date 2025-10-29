# Arquivo: tests/conftest.py
# Descrição: Configurações globais e fixtures para testes

import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture(scope="module")
def client():
    """Cria um cliente de teste da aplicação FastAPI"""
    return TestClient(app)
