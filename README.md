# Layer API

API REST de reviews de perfumes, inspirada no Fragrantica, construída com FastAPI.

> 🚧 Projeto em desenvolvimento

## Tecnologias

- Python 3.14
- FastAPI
- pytest
- Ruff

## Como rodar localmente

```bash
git clone https://github.com/tassohenrique/layer-api.git
cd layer-api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
fastapi dev app/main.py
```

A documentação interativa fica em http://127.0.0.1:8000/docs

## Testes

```bash
python -m pytest -v
```