import sqlite3
import os

DATABASE_URL = "sisdiv.db"

def get_db():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    if not os.path.exists(DATABASE_URL):
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Tabela de simulações
        cursor.execute('''
            CREATE TABLE simulacoes (
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
