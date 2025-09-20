from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import os
from datetime import datetime
from calcular_sac import calcular_sac
from calcular_price import calcular_price
from calculo_pagamento_variavel import calculo_pagamento_variavel

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
        conn = sqlite3.connect("sisdiv.db")
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
        conn = sqlite3.connect("sisdiv.db")
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

@app.post("/calcular/")
async def calcular_amortizacao(
    valor: float = Form(...),
    taxa: float = Form(...),
    prazo: int = Form(...),
    carencia: int = Form(0),
    metodo: str = Form("ambos"),
    salvar: bool = Form(False),
    db: sqlite3.Connection = Depends(get_db)
):
    try:
        taxa_decimal = taxa / 100
        
        resultado = {}
        
        if metodo in ["sac", "ambos"]:
            temcarencia = 1 if carencia != 0 else 0
            resultado["sac"] = calcular_sac(valor, taxa_decimal, prazo, carencia, temcarencia)
        
        if metodo in ["price", "ambos"]:
            temcarencia = 1 if carencia != 0 else 0
            resultado["price"] = calcular_price(valor, taxa_decimal, prazo, carencia, temcarencia)
        
        if salvar:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO simulacoes (valor, taxa, prazo, carencia, metodo, data_criacao) VALUES (?, ?, ?, ?, ?, ?)",
                (valor, taxa, prazo, carencia, metodo, datetime.now())
            )
            db.commit()
            resultado["simulacao_id"] = cursor.lastrowid
        
        return JSONResponse(content=resultado)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no cálculo da amortização: {str(e)}"
        )

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
        resultados = {}
        
        if simulacao[5] in ["sac", "ambos"]:
            resultados["sac"] = calcular_sac(simulacao[1], taxa_decimal, simulacao[3], simulacao[4])
        
        if simulacao[5] in ["price", "ambos"]:
            resultados["price"] = calcular_price(simulacao[1], taxa_decimal, simulacao[3], simulacao[4])
        
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
