from typing import Optional
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import sqlite3
import os
from datetime import datetime
from src.calculadoras.calcular_sac import calcular_sac
from src.calculadoras.calcular_sam import calcular_sam
from src.calculadoras.calcular_price import calcular_price
from src.calculadoras.calculo_pagamento_variavel import calculo_pagamento_variavel
from src.calculadoras.comparacao_SELIC import simular_comparacao_SELIC

app = FastAPI(title="Sisdiv - Sistema de Amortização de Dívidas")

# Criar diretórios se não existirem
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Configuração de templates e arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Inicializar banco de dados
def init_db():
    try:
        conn = sqlite3.connect("sisdiv.db", check_same_thread=False)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS simulacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                valor REAL NOT NULL,
                taxa REAL NOT NULL,
                prazo INTEGER NOT NULL,
                carencia INTEGER DEFAULT 0,
                metodo TEXT NOT NULL,
                data_criacao DATETIME NOT NULL
            )
        ''')

        conn.commit()
        conn.close()
        print("Banco de dados inicializado com sucesso!")
    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {e}")


init_db()


def get_db():
    try:
        conn = sqlite3.connect("sisdiv.db", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro de conexão com o banco de dados: {str(e)}"
        )


# Rotas da aplicação
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao carregar página inicial: {str(e)}"
        )


def calcular_resultados_amortizacao(valor, taxa_decimal, prazo, carencia=0, metodo="ambos", temcarencia=None):
    """
    Calcula os resultados de amortização para SAC, Price ou ambos.
    """
    resultados = {}
    if temcarencia is None:
        temcarencia = 1 if carencia != 0 else 0

    if metodo in ["sac", "ambos"]:
        resultados["sac"] = calcular_sac(valor, taxa_decimal, prazo, carencia, temcarencia)
    if metodo in ["price", "ambos"]:
        resultados["price"] = calcular_price(valor, taxa_decimal, prazo, carencia, temcarencia)
    if metodo in ["sam", "ambos"]:
        resultados["sam"] = calcular_sam(valor, taxa_decimal, prazo, carencia, temcarencia)
    if metodo in ["pagamento_variavel", "ambos"]:
        resultados["pagamento_variavel"] = calculo_pagamento_variavel(valor, taxa_decimal, prazo, carencia, temcarencia)
    return resultados


@app.post("/calcular/")
async def calcular_amortizacao(
        valor: float = Form(...),
        taxa: float = Form(...),
        prazo: int = Form(...),
        carencia: int = Form(0),
        metodo: str = Form("ambos"),
        db: sqlite3.Connection = Depends(get_db)
):
    try:
        taxa_decimal = taxa / 100
        temcarencia = 1 if carencia != 0 else 0
        resultado = calcular_resultados_amortizacao(valor, taxa_decimal, prazo, carencia, metodo, temcarencia)
        return JSONResponse(content=resultado)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no cálculo da amortização: {str(e)}"
        )


@app.post("/investimentos/")
def simular_investimentos(
        valor_investido: float = Form(...),
        prazo_anos: int = Form(...),
        percentual_base: dict = Form(...),
        taxa_atual_SELIC: Optional[float] = Form(None)
):
    """
    Simula diferentes tipos de investimentos com base na taxa SELIC atual
    ou uma taxa fornecida manualmente.

    Exemplo de percentual_base:
    percentual_base = {
        "Tesouro Selic": 1.0,
        "CDB Banco X": 1.1,
        "LCA Banco Y": 0.95
    }
    """
    try:
        resultado = simular_comparacao_SELIC(
            percentual_base=percentual_base,
            prazo_anos=prazo_anos,
            valor_investido=valor_investido,
            taxa_atual_SELIC=taxa_atual_SELIC
        )

        return JSONResponse(content=resultado)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Erro na simulação de investimentos: {str(e)}")


@app.get("/simulacoes/", response_class=HTMLResponse)
async def listar_simulacoes(request: Request, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM simulacoes ORDER BY data_criacao DESC")
        simulacoes = cursor.fetchall()

        # Converter para lista de dicionários para facilitar no template
        simulacoes_list = []
        for sim in simulacoes:
            simulacoes_list.append({
                "id": sim[0],
                "valor": sim[1],
                "taxa": sim[2],
                "prazo": sim[3],
                "carencia": sim[4],
                "metodo": sim[5],
                "data_criacao": sim[6]
            })

        return templates.TemplateResponse("simulacoes.html", {
            "request": request,
            "simulacoes": simulacoes_list
        })

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar simulações: {str(e)}"
        )


@app.get("/simulacao/{simulacao_id}", response_class=HTMLResponse)
async def ver_simulacao(request: Request, simulacao_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM simulacoes WHERE id = ?", (simulacao_id,))
        simulacao = cursor.fetchone()

        if not simulacao:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error": "Simulação não encontrada"
            })

        # Recalcular os dados
        taxa_decimal = simulacao[2] / 100
        temcarencia = 1 if simulacao[4] != 0 else 0
        resultados = calcular_resultados_amortizacao(
            simulacao[1], taxa_decimal, simulacao[3], simulacao[4], simulacao[5], temcarencia
        )

        return templates.TemplateResponse("amortizacao.html", {
            "request": request,
            "valor": simulacao[1],
            "taxa": simulacao[2],
            "prazo": simulacao[3],
            "carencia": simulacao[4],
            "metodo": simulacao[5],
            "resultados": resultados
        })

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao carregar simulação: {str(e)}"
        )


@app.post("/simulacao/{simulacao_id}/delete")
async def deletar_simulacao(simulacao_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM simulacoes WHERE id = ?", (simulacao_id,))
        db.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Simulação não encontrada")

        # Redirect back to the simulations page
        return RedirectResponse(url="/simulacoes/", status_code=303)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao deletar simulação: {str(e)}"
        )


@app.post("/salvar_simulacao")
async def salvar_simulacao(
        valor: float = Form(...),
        taxa: float = Form(...),
        prazo: int = Form(...),
        carencia: int = Form(...),
        metodo: str = Form(...),
        db: sqlite3.Connection = Depends(get_db)
):
    try:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO simulacoes (valor, taxa, prazo, carencia, metodo, data_criacao) VALUES (?, ?, ?, ?, ?, ?)",
            (valor, taxa, prazo, carencia, metodo, datetime.now().strftime("%d-%m-%Y"))
        )
        db.commit()

        return RedirectResponse("/simulacoes/", status_code=303)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar simulação: {str(e)}"
        )


# --- ROTA DE HEALTH CHECK ---
@app.get("/healthcheck")
async def healthcheck(db: sqlite3.Connection = Depends(get_db)):
    import time
    inicio = time.time()

    try:
        cursor = db.cursor()
        cursor.execute("SELECT 1")  # testa o banco
        db_status = "ok"
    except Exception as e:
        db_status = f"erro: {str(e)}"

    fim = time.time()

    return {
        "status": "ok",
        "api": "online",
        "database": db_status,
        "latencia_ms": round((fim - inicio) * 1000, 2)
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)