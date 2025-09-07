from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SimulacaoCreate(BaseModel):
    valor: float
    taxa: float
    prazo: int
    carencia: int = 0
    metodo: str = "ambos"

class Simulacao(SimulacaoCreate):
    id: int
    data_criacao: datetime

class AmortizacaoResult(BaseModel):
    parcela: int
    prestacao: float
    juros: float
    amortizacao: float
    saldo_devedor: float
