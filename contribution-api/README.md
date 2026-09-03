# Project Volusia — Contribution API Server

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
python -m app.main
```

The server runs on http://0.0.0.0:8899 by default.

## API Docs

- Swagger UI: http://localhost:8899/docs
- ReDoc: http://localhost:8899/redoc
- OpenAPI JSON: http://localhost:8899/openapi.json

## Project Structure

```
contribution-api/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app, lifespan, middleware
│   ├── config.py         # Pydantic settings (env vars)
│   ├── database.py       # SQLAlchemy session + init_db
│   ├── models.py         # ORM models (Contributor, Submission, AgentItem, APILog)
│   └── routers/
│       ├── auth.py       # /api/v1/auth/* (register, login, me, revoke)
│       ├── submissions.py # /api/v1/submissions/* (F, I, agent-item, status, list)
│       ├── data.py       # /api/v1/data/* (sources, tables, samples, metadata)
│       └── contributors.py # /api/v1/contributors/me/record
├── requirements.txt
├── .env.example
└── README.md
```

## Database

Defaults to SQLite (`sqlite:///./volusia_api.db`). For production, set `DATABASE_URL` to a Postgres connection string in `.env`.

## Authentication

- **API Keys:** Issued at registration, passed as `Authorization: Bearer <api_key>`
- **Bearer Tokens:** Issued at login (24h expiry, refresh token for 30 days)
- **Anonymous:** No auth required for public endpoints (future)

## Rate Limiting

Per-key, per-endpoint-category, per-time-window. See `config.py` for defaults.

## Environment Variables

See `.env.example` for all configurable values.

## License

MIT
