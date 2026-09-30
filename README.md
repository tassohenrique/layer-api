# Layer API
API REST de reviews de perfumes, inspirada no Fragrantica, construída com FastAPI e PostgreSQL.


**🚀 API no ar:** [layer-api-xxxx.onrender.com/docs](https://layer-api-xxxx.onrender.com/docs)

> A hospedagem é gratuita e entra em repouso sem uso. A primeira requisição pode levar cerca de um minuto; depois disso, responde normalmente.

[![CI](https://github.com/tassohenrique/layer-api/actions/workflows/ci.yml/badge.svg)](https://github.com/tassohenrique/layer-api/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791)
![Cobertura](https://img.shields.io/badge/cobertura-99%25-brightgreen)

> 🚧 Projeto em desenvolvimento

## Tecnologias

- Python 3.14
- FastAPI
- PostgreSQL 17
- SQLAlchemy 2.0
- Docker / Docker Compose
- pytest
- Ruff
- Deploy: Render (API em container Docker) + Neon (PostgreSQL gerenciado)

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

## Criando um administrador

Rotas de escrita (cadastrar, editar e apagar marcas, notas e perfumes) exigem um usuário administrador. Para criar um, ou promover um usuário existente:

```bash
python -m scripts.create_admin --email admin@exemplo.com --name "Admin"
```


A documentação interativa fica em http://127.0.0.1:8000/docs

## Testes

Os testes usam um banco separado. Crie ele uma única vez:

```bash
docker compose exec db createdb -U layer layer_test
```

Depois rode:

```bash
python -m pytest -v
```

Para ver a cobertura de testes:

```bash
python -m pytest --cov=app --cov-report=term-missing
```

A cada push na branch `main`, o GitHub Actions roda o lint, aplica as migrations num banco limpo e executa todos os testes.