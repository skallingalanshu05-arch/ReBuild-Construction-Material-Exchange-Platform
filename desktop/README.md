# ReBuild — desktop Tkinter client

Desktop UI that connects to the **ReBuild FastAPI backend** so listings are stored in **MongoDB**.

## Flow (like a real app)

1. **Start the app** — you see **Sign in** and **Register** only (no listing tabs yet).
2. **Register** — create user + company, or **Sign in** with existing email/password.
3. After success — **Register surplus**, **Search & match**, and **All listings** appear; header shows your email and **Sign out**.
4. **Sign out** — returns to the login/register screen.

If `desktop/session.json` has a valid token from a previous run, the app opens straight to the main tabs.

## Requirements

- Python **3.11+** with Tkinter
- **Backend running** (`backend/` — `python run.py`)
- **MongoDB** running (local or Atlas in `backend/.env`)

## Setup

1. Start MongoDB and the API:

```powershell
cd backend
.\.venv\Scripts\python.exe run.py
```

2. Copy config (optional — default URL is fine on same PC):

```powershell
cd desktop
copy config.example.json config.json
```

3. Run the desktop app:

```powershell
python desktop\app.py
```

4. On the welcome screen: **Register** tab or **Sign in** tab. Password rules: 8+ chars, upper, lower, digit (e.g. `SecurePass1`). This is **not** your MongoDB URL or password.

Web alternative: http://localhost:5173/register or `/login` with `npm run dev` in `frontend/`.

## Where data is stored

| Action | Storage |
|--------|---------|
| **Save listing** | `POST /materials` → MongoDB `materials` collection |
| **All listings** | `GET /materials/my-listings` (your company) |
| **Search & match** | `GET /materials` (active listings on platform) + local scoring |
| **Session token** | `desktop/session.json` (local file, not committed) |

## Material types → MongoDB

Fixed types (Window frame, Door frame, Steel, Brick, Aggregate) map to seeded **categories** and API units (`PIECE`, `TONNE`, `KG`, `CUBIC_METER`).

## Main tabs (after sign-in)

1. **Register surplus** — saves materials to MongoDB  
2. **Search & match** — loads listings from API  
3. **All listings** — your company's rows from MongoDB  

| Material | Default unit |
|----------|----------------|
| Window frame | nos (pieces) |
| Door frame | nos (pieces) |
| Steel | ton or kg (dropdown) |
| Brick | nos (pieces) |
| Aggregate | m³ (cubic metre) |

Choosing a type updates the quantity label and unit automatically.
