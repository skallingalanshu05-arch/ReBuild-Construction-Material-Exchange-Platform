# ReBuild — Construction Material Exchange Platform

Monorepo for the **ReBuild** digital platform for resource reuse and matching (construction and demolition materials).

| Package | Path | Stack |
|--------|------|--------|
| **Frontend** | [`frontend/`](./frontend/) | Vite, TanStack Start/Router, React, Tailwind |
| **Backend API** | [`backend/`](./backend/) | FastAPI, MongoDB, JWT |

The UI is based on [pixel-perfect-replica](https://github.com/skallingalanshu05-arch/pixel-perfect-replica) and lives under `frontend/`.

## Quick start

### Backend

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

API docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
cp .env.example .env
bun install   # or: npm install
bun run dev   # or: npm run dev
```

Set `VITE_API_BASE_URL=http://localhost:8000/api/v1` in `frontend/.env` if you are not using the Vite dev proxy (default in dev is `/api/v1` → `http://127.0.0.1:8000`).

### From repo root

```bash
npm install          # installs frontend workspace dependencies
npm run dev:frontend
```

## Repository layout

```
.
├── frontend/          # React app (pixel-perfect-replica)
├── backend/           # FastAPI REST API
├── index.py           # Legacy CLI prototype (optional)
├── package.json       # npm workspaces root
└── README.md
```

## Legacy CLI

The root `index.py` file is an early console prototype for surplus material registration and matching. The production path is **frontend + backend**.
