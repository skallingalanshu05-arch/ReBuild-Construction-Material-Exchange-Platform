# Pixel Perfect Replica — desktop Tkinter client

Offline-capable UI that connects to the **ReBuild FastAPI backend** so listings are stored in **MongoDB**.

## Requirements

- Python **3.11+** with Tkinter
- **Backend running** (`backend/` — `python run.py`)
- **MongoDB** running (local or Atlas in `backend/.env`)
- A **user account** with a **company** (register on web or API — supplier capability)

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

4. Open the **Account** tab → confirm API URL → **Sign in** with your ReBuild email/password.

## Where data is stored

| Action | Storage |
|--------|---------|
| **Save listing** | `POST /materials` → MongoDB `materials` collection |
| **All listings** | `GET /materials/my-listings` (your company) |
| **Search & match** | `GET /materials` (active listings on platform) + local scoring |
| **Session token** | `desktop/session.json` (local file, not committed) |

## Material types → MongoDB

Fixed types (Window frame, Door frame, Steel, Brick, Aggregate) map to seeded **categories** and API units (`PIECE`, `TONNE`, `KG`, `CUBIC_METER`).

## Tabs

1. **Account** — API URL, sign in/out  
2. **Register surplus** — saves to MongoDB (requires sign-in)  
3. **Search & match** — loads listings from API  
4. **All listings** — your company's rows from MongoDB  

| Material | Default unit |
|----------|----------------|
| Window frame | nos (pieces) |
| Door frame | nos (pieces) |
| Steel | ton or kg (dropdown) |
| Brick | nos (pieces) |
| Aggregate | m³ (cubic metre) |

Choosing a type updates the quantity label and unit automatically.
