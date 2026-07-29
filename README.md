# backend

Projeto backend — estrutura mínima para rodar a API.

Como rodar localmente:

```bash
python -m venv .venv
source .venv/bin/activate   # ou .venv\Scripts\Activate.ps1 no Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Arquivos principais: `app/main.py`, `app/api/`.
