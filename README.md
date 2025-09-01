# Sisdiv
Sistema de Amortização de Dívidas. Aplicativo web desenvolvido com FastAPI e modelos Jinja2.

## Recursos

- Adicionar, visualizar e gerenciar itens de tarefas
- Interface responsiva com CSS personalizado
- Backend FastAPI com templates Jinja2
- Arquivo estático para estilos

## Estrutura do Projeto

```
main.py
requirements.txt
static/
style.css
templates/
base.html
index.html
todo_item.html
```

## Instalação

1. Clone o repositório:

```sh
git clone <url-do-seu-repositório>
cd <diretório-do-projeto>
```

2. Instale as dependências:

```sh
pip install -r requirements.txt
```

## Executando a Aplicação

Inicie o servidor FastAPI usando o Uvicorn:

```sh
uvicorn main:app --reload
```

Em seguida, abra [http://localhost:8000](http://localhost:8000) no seu navegador.

## Dependências

Consulte [requirements.txt](requirements.txt) para a lista completa.

- fastapi
- uvicorn
- Jinja2
- pydantic
- python-multipart

## Licença
