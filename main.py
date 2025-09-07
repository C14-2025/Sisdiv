from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import os
from datetime import datetime

app = FastAPI(title="Sisdiv - Sistema de Amortização de Dívidas")

# Criar diretórios se não existirem
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Configuração de templates e arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Inicializar banco de dados
def init_db():
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

init_db()

def get_db():
    conn = sqlite3.connect("sisdiv.db")
    try:
        yield conn
    finally:
        conn.close()

# Funções de cálculo de amortização
def calcular_sac(valor: float, taxa: float, prazo: int, carencia: int = 0):
    dados = []
    amortizacao = valor / prazo
    saldo_devedor = valor

    for i in range(1, carencia + 1):
        juros = saldo_devedor * taxa
        prestacao = juros
        dados.append({
            "parcela": i,
            "prestacao": prestacao,
            "juros": juros,
            "amortizacao": 0,
            "saldo_devedor": saldo_devedor
        })

    for i in range(carencia + 1, carencia + prazo + 1):
        juros = saldo_devedor * taxa
        prestacao = juros + amortizacao
        saldo_devedor -= amortizacao

        dados.append({
            "parcela": i,
            "prestacao": prestacao,
            "juros": juros,
            "amortizacao": amortizacao,
            "saldo_devedor": max(0, saldo_devedor)
        })

    return dados

def calcular_price(valor: float, taxa: float, prazo: int, carencia: int = 0):
    dados = []
    saldo_devedor = valor

    for i in range(1, carencia + 1):
        juros = saldo_devedor * taxa
        prestacao = juros
        dados.append({
            "parcela": i,
            "prestacao": prestacao,
            "juros": juros,
            "amortizacao": 0,
            "saldo_devedor": saldo_devedor
        })

    if prazo > 0:
        prestacao_fixa = (valor * taxa * (1 + taxa) ** prazo) / ((1 + taxa) ** prazo - 1)
    else:
        prestacao_fixa = 0

    for i in range(carencia + 1, carencia + prazo + 1):
        juros = saldo_devedor * taxa
        amortizacao = prestacao_fixa - juros
        saldo_devedor -= amortizacao

        dados.append({
            "parcela": i,
            "prestacao": prestacao_fixa,
            "juros": juros,
            "amortizacao": amortizacao,
            "saldo_devedor": max(0, saldo_devedor)
        })

    return dados

# Rotas da aplicação
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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
    taxa_decimal = taxa / 100
    
    resultado = {}
    
    if metodo in ["sac", "ambos"]:
        resultado["sac"] = calcular_sac(valor, taxa_decimal, prazo, carencia)
    
    if metodo in ["price", "ambos"]:
        resultado["price"] = calcular_price(valor, taxa_decimal, prazo, carencia)
    
    if salvar:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO simulacoes (valor, taxa, prazo, carencia, metodo, data_criacao) VALUES (?, ?, ?, ?, ?, ?)",
            (valor, taxa, prazo, carencia, metodo, datetime.now())
        )
        db.commit()
        resultado["simulacao_id"] = cursor.lastrowid
    
    return JSONResponse(content=resultado)

@app.get("/simulacoes/", response_class=HTMLResponse)
async def listar_simulacoes(request: Request, db: sqlite3.Connection = Depends(get_db)):
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

@app.get("/simulacao/{simulacao_id}", response_class=HTMLResponse)
async def ver_simulacao(request: Request, simulacao_id: int, db: sqlite3.Connection = Depends(get_db)):
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
