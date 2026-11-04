# ReBuild API Backend

Production-minded FastAPI backend for the **ReBuild** construction and demolition material resource exchange platform. It exposes versioned REST APIs for a separate React frontend.

## Technology stack

- Python 3.11+
- FastAPI, Uvicorn
- MongoDB with PyMongo `AsyncMongoClient`
- Pydantic v2 and Pydantic Settings
- JWT access/refresh tokens, Argon2 password hashing
- Pytest and HTTPX for API tests

## Project structure

```
backend/
├── app/
│   ├── main.py
│   ├── core/           # config, security, permissions, exceptions
│   ├── database/       # connection, indexes, seed data
│   ├── models/         # enums and domain constants
│   ├── schemas/        # request/response validation
│   ├── api/v1/         # REST endpoints
│   ├── services/       # business logic (auth, matching, requests, …)
│   └── utils/
├── tests/
├── scripts/create_admin.py
├── requirements.txt
├── .env.example
└── run.py
```

## Setup

Use **Python 3.11 or 3.12** (recommended). Python 3.15+ often breaks dependency installs on Windows.

### macOS / Linux

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MongoDB URL and JWT secret
```

### Windows (PowerShell)

```powershell
cd backend
# Prefer 3.12 if installed: py -3.12 -m venv .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
copy .env.example .env
python run.py
```

You must see `(.venv)` in the prompt **before** `pip install` and `python run.py`. Installing without activating the venv puts packages on the wrong Python and `uvicorn` will not be found.

If `Activate.ps1` is blocked: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

Verify the venv is active:

```powershell
python -c "import sys; print(sys.executable)"
# Should end with ...\backend\.venv\Scripts\python.exe
```

### MongoDB

Install MongoDB locally or use Atlas. Default connection:

`mongodb://localhost:27017` with database `rebuild_db`.

**Multi-document transactions** (recommended for strict reservation semantics) require a replica set. Set `MONGODB_SUPPORTS_TRANSACTIONS=true` when using a replica set. On standalone MongoDB, the API uses conditional atomic updates and rejects confirmations when quantity is insufficient.

### Create administrator

Administrators cannot register via the public API.

```bash
python scripts/create_admin.py
```

### Run the server

```bash
uvicorn app.main:app --reload
# or
python run.py
```

- Health: `GET http://localhost:8000/health`
- Swagger: `http://localhost:8000/docs`

## Environment variables

See `.env.example` for all settings (`MONGODB_URL`, `JWT_SECRET_KEY`, `CORS_ORIGINS`, etc.).

## API overview (base: `/api/v1`)

| Area | Endpoints |
|------|-----------|
| Auth | `POST /auth/register`, `/login`, `/refresh`, `/logout`, `GET /me`, password reset |
| Companies | `POST /companies`, `GET/PATCH /companies/me`, `GET /companies/{id}` |
| Projects | CRUD under `/projects` |
| Categories | `GET /categories`, admin create/update/deactivate |
| Materials | CRUD, search, `/materials/my-listings` |
| Requirements | CRUD, search, `/requirements/my-requirements` |
| Matching | `GET /matches/requirement/{id}`, `/matches/material/{id}` |
| Requests | Workflow: create, accept, reject, negotiate, confirm, cancel |
| Transactions | List, detail, complete |
| Notifications | List, read, read-all, delete |
| Admin | Dashboard, users, companies, moderation lists |

## Matching engine

Implemented in `app/services/matching_service.py` with weighted scoring:

- Material type (30), quantity (25), condition (20), location (15), availability (10)

Supports full/partial matches, Haversine distance, city fallback, and sort options.

## Tests

Uses isolated database `rebuild_test_db` (override with `MONGODB_DATABASE`).

```bash
pytest -v
```

## React frontend integration

Set `CORS_ORIGINS` to your Vite dev server (default `http://localhost:5173`). Send `Authorization: Bearer <access_token>` on protected routes. Refresh tokens via `POST /api/v1/auth/refresh`.

## Example: register and list materials

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Demo","email":"demo@example.com","mobile_number":"9999999999","password":"SecurePass1"}'
```

Use the returned `access_token` for subsequent calls.
