# Layer API

API REST de reviews de perfumes, inspirada no Fragrantica, construída com FastAPI e PostgreSQL.

> 🚧 Projeto em desenvolvimento

## Tecnologias

- Python 3.14
- FastAPI
- PostgreSQL 17
- SQLAlchemy 2.0
- Docker / Docker Compose
- pytest
- Ruff

## Como rodar localmente

Pré-requisitos: Python 3.12+ e Docker.

```bash
git clone https://github.com/tassohenrique/layer-api.git
cd layer-api

# Variáveis de ambiente
cp .env.example .env

# Banco de dados
docker compose up -d
alembic upgrade head

# Ambiente Python
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt

# API
fastapi dev app/main.py
```

A documentação interativa fica em http://127.0.0.1:8000/docs

## Testes

```bash
python -m pytest -v
```