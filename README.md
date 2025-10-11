# Sisdiv
Sistema de Amortização de Dívidas. Aplicativo web desenvolvido com FastAPI e modelos Jinja2.

## Recursos

- Adicionar, visualizar e gerenciar itens de tarefas
- Interface responsiva com CSS personalizado
- Backend FastAPI com templates Jinja2
- Arquivo estático para estilos
- Fluxo de Caixa e Impacto de Dívidas
- Gera um relatório detalhado e um gráfico visual (`fluxo_caixa_projecao_exemplo.png`- salvo na pasta 'static/' para consumo pelo frontend).

## Estrutura do Projeto

```
sisdiv/
├── main.py
├── test_main.py
├── requirements.txt
├── static/
│ └── style.css
├── templates/
│ ├── base.html
│ ├── index.html
│ ├── amortizacao.html
│ └── simulacoes.html
├── fluxo_caixa.py
└── README.md
```

## Instalação

1. Clone o repositório:

```bash
git clone <url-do-seu-repositório>
cd <diretório-do-projeto>
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Executando a Aplicação

Inicie o servidor FastAPI usando o Uvicorn:

```bash
uvicorn main:app --reload
```

Em seguida, abra [http://localhost:8000](http://localhost:8000) no seu navegador.

Executando Testes
Para executar os testes unitários:

```bash
python -m pytest tests/test_main.py -v
```

Ou execute diretamente:

python test_main.py

Desenvolvimento
O sistema inclui testes unitários que validam:

Cálculos corretos do método SAC

Cálculos corretos do método Price

Comparação entre os dois métodos

Verificação de que SAC é mais vantajoso no total pago

## Dependências

Consulte [requirements.txt](requirements.txt) para a lista completa.

- fastapi
- uvicorn
- Jinja2
- pydantic
- python-multipart

## Licença
