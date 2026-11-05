# ReBuild — Project guide for civil engineering students

**You do not need to be a programmer to understand this project.**  
This document explains *what* ReBuild does on a construction site, *why* it matters, and *how* the different parts of the software work together — in everyday language.

---

## 1. What problem does ReBuild solve?

On construction and demolition (C&D) projects, companies often have:

- **Surplus** — extra bricks, steel, frames, aggregate, timber left after a job or from partial demolition  
- **Shortage** — another site needs similar materials but would buy new from the market  

Today, much reusable material goes to **landfill** or sits unused in yards. That wastes money, energy, and natural resources.

**ReBuild** is a **digital exchange platform**: companies **list** what they have, **post** what they need, and the system **suggests good pairings** (matches) based on type, quantity, quality, location, timing, and budget — similar to how you might compare suppliers for a BOQ item, but focused on **reuse**.

This supports:

- **Circular economy** in construction  
- **Lower cost** for the buyer  
- **Less C&D waste** and better sustainability metrics on projects  

---

## 2. Who uses the platform?

| Role (in the app) | Real-world example |
|-------------------|-------------------|
| **Construction company / supplier** | Contractor A finishes a block; has 500 surplus bricks and steel door frames |
| **Construction company / buyer** | Contractor B starts a low-rise project; needs bricks and frames nearby |
| **Platform admin** | Manages categories, users, and system settings (backend) |

Users **register** with their **company** (not as random individuals). After login they can manage **projects**, **listings**, **requirements**, **matches**, and **requests** to connect with another company.

---

## 3. How work flows on the site (business process)

Think of four steps — the same idea appears on the website home page:

```text
  LIST SURPLUS  →  POST NEED  →  GET MATCHES  →  REQUEST & REUSE
     (supply)        (demand)      (ranking)         (handshake)
```

1. **List surplus** — Supplier enters material type, quantity, unit (nos, tonne, m³), condition (Poor → Excellent), location, when it is available, and price (or free).  
2. **Post requirement** — Buyer enters what they need, minimum acceptable condition, quantity, preferred location, how far they will haul, latest date needed, and max budget.  
3. **Get matched** — Software scores each possible supplier listing against the requirement and shows the **best fits first**.  
4. **Agree & reuse** — Buyer sends a **request**; both sides can message, agree, and record the exchange (requests / transactions in the full system).

---

## 4. The matching score (this is the “mini project brain”)

The platform does **not** randomly suggest materials. It uses a **scoring model** (like weighted criteria in a technical bid).

For each pair (your requirement ↔ someone else’s listing), points are added roughly as follows:

| Factor | Max points | Civil interpretation |
|--------|------------|----------------------|
| **Material type** | 30 | Same type (e.g. “Brick”) scores highest; same category but different subtype scores less |
| **Quantity** | 25 | Can the listing fully cover your need? Partial supply gets partial points |
| **Condition / quality** | 20 | Listing condition vs your minimum (Poor / Fair / Good / Excellent). Too poor may be rejected unless you allow lower quality |
| **Location / distance** | 15 | Closer sites score higher (uses map coordinates when available; otherwise city name) |
| **Availability / time** | 10 | Material ready **on or before** your required date scores higher |

**Total** is out of about **100**. Labels:

- **80+** — Highly suitable  
- **60–79** — Moderately suitable  
- **Below 60** — Low suitability  

Filters also apply: wrong category, wrong unit, inactive listing, over budget, or beyond max distance → that listing is **not shown**.

The same logic started in a simple **console program** (`index.py` at repo root) and was expanded in the **backend** (`backend/app/services/matching_service.py`).

---

## 5. Important words (construction ↔ software)

| Term in the app | What it means on site |
|-----------------|------------------------|
| **Listing / material** | A surplus offer (what is available for reuse) |
| **Requirement** | What your project still needs to buy or source |
| **Match** | A scored link between one requirement and one listing |
| **Request** | Formal interest: “We want to take this material from you” |
| **Project** | A job site or contract you link listings/requirements to |
| **Category** | Group: bricks & masonry, steel, timber, fixtures, etc. |
| **Unit** | nos (pieces), tonne, kg, m³ — must match between need and supply |
| **Listing status** | Draft → Active (visible for matching) |
| **JWT / login** | Electronic **site pass**: proves who you are after email + password |

---

## 6. Parts of this repository (three faces, one idea)

The project folder contains **three ways** to use the same ReBuild idea:

### A. Website — `frontend/`

- What you **see and click** in the browser (pages, forms, tables).  
- **Analogy:** Site office **notice board + forms** — modern, visual, for daily use.  
- Runs at `http://localhost:5173` when developers start it (`npm run dev` or `bun run dev`).

### B. Server / API — `backend/`

- The **brain and filing cabinet** behind the website (and desktop app).  
- Stores users, companies, materials, requirements, matches in **MongoDB** (a database — like a structured digital register).  
- **Analogy:** Head office **registers, rules, and calculations** — matching scores, security, who may see what.  
- Runs at `http://localhost:8000` (`python run.py` inside `backend/`).  
- Interactive API documentation: `http://localhost:8000/docs` (for developers).

### C. Desktop app — `desktop/`

- A **small window program** (Python + Tkinter) for demos or labs.  
- Same login and listings as the server, but simpler screens: register surplus, search & match, your listings.  
- **Analogy:** A **portable kiosk** on one PC — good for mini project demo without opening a browser.

### D. Old console demo — `index.py` (root)

- Early **text-only** version in the terminal: type answers, see match scores.  
- **Analogy:** Hand calculation **before** Excel — same concept, no graphics.

**For a full demo:** run **MongoDB** + **backend** + either **frontend** or **desktop**.

---

## 7. Complete folder structure (updated)

This is the **map of the project folder** on your computer or GitHub. You do not need to open every file — but in a viva you can point to **where** login, matching, and listings live.

### 7.1 Big picture

```text
ReBuild-Construction-Material-Exchange-Platform/
│
├── README.md                          → How developers install and run everything
├── PROJECT_GUIDE_FOR_CIVIL_ENGINEERS.md → This guide (non-coder friendly)
├── package.json                       → Root script to start the website from one command
├── index.py                           → Old text-only demo (matching in the terminal)
│
├── backend/                           → Server + database logic (Python)
├── frontend/                          → Website in the browser (React)
└── desktop/                           → Small desktop window app (Python + Tkinter)
```

**Analogy:** One construction **project site** (`ReBuild-…-Platform/`) with three **sub-contractors**: `backend` (office + records), `frontend` (client-facing showroom), `desktop` (site kiosk).

---

### 7.2 Root files (top level)

| File / folder | What it does |
|---------------|--------------|
| `README.md` | Step-by-step setup: Python venv, `pip install`, MongoDB, run server and website. |
| `PROJECT_GUIDE_FOR_CIVIL_ENGINEERS.md` | Plain-language explanation for civil students (you are here). |
| `package.json` | Lists npm scripts; e.g. `npm run dev:frontend` starts the web app from repo root. |
| `index.py` | **First mini-project version:** no browser, no database — you type answers in a black terminal window and see match scores. |
| `.gitignore` | Tells Git which files **not** to upload (passwords, local `.env`, virtual env folder). |

---

### 7.3 Backend folder (`backend/`)

The **server** that saves data and calculates matches. Everything under `backend/app/` is the main application.

```text
backend/
├── run.py                 → START button for the server (runs on port 8000)
├── requirements.txt       → Shopping list for pip (FastAPI, uvicorn, MongoDB driver, …)
├── .env.example           → Sample settings (database URL, secrets); copy to `.env`
├── pytest.ini             → Settings for automated tests
├── README.md              → Backend-specific notes for developers
│
├── scripts/
│   └── create_admin.py    → One-time tool to create an admin user
│
├── tests/                 → Automatic checks that login, materials, matching work
│   ├── test_auth.py
│   ├── test_materials.py
│   ├── test_matching.py
│   └── …
│
└── app/
    ├── main.py            → App entry: wires routes, CORS, startup
    │
    ├── core/              → Rules of the house
    │   ├── config.py      → Reads `.env` (MongoDB URL, JWT secret, …)
    │   ├── security.py    → Password hashing, JWT tokens
    │   ├── permissions.py → Who can do what (admin vs company user)
    │   └── exceptions.py  → Standard error messages
    │
    ├── database/
    │   ├── connection.py  → Connects to MongoDB
    │   ├── seed.py        → Fills initial categories (brick, steel, …)
    │   └── indexes.py     → Speeds up searches in the database
    │
    ├── models/            → **Shape of stored records** (like blank forms in the register)
    │   ├── user.py        → User accounts
    │   ├── company.py     → Construction companies
    │   ├── material.py    → Surplus listings
    │   ├── requirement.py → Buyer needs
    │   ├── project.py     → Job sites linked to listings
    │   ├── request.py     → “We want this material” messages
    │   ├── match.py       → Match result types / labels
    │   └── …
    │
    ├── schemas/           → **Validation** for data coming in/out of the API (checked fields)
    │
    ├── services/          → **Business logic** (the real work)
    │   ├── matching_service.py  → ⭐ Scoring algorithm (type, qty, condition, location, time)
    │   ├── material_service.py  → Create/update listings
    │   ├── auth_service.py      → Register, login, tokens
    │   ├── request_service.py   → Material requests between companies
    │   └── …
    │
    ├── api/
    │   ├── deps.py        → “Is this user logged in?” helpers
    │   └── v1/
    │       ├── router.py  → Connects all URL groups
    │       └── endpoints/ → One file per feature area
    │           ├── auth.py
    │           ├── materials.py
    │           ├── requirements.py
    │           ├── matches.py
    │           ├── requests.py
    │           ├── companies.py
    │           └── …
    │
    └── utils/             → Small shared helpers (pagination, IDs, API responses)
```

**For your report:** Say that **`matching_service.py`** implements the civil-engineering-relevant **decision logic**; **`materials.py` / `requirements.py`** are the API “counters” where listings and needs are submitted.

---

### 7.4 Frontend folder (`frontend/`)

The **website** users see in Chrome/Edge. Built with **React** (many reusable UI pieces).

```text
frontend/
├── package.json           → Website dependencies; scripts: `dev`, `build`, `test`
├── vite.config.ts         → Dev server (often http://localhost:5173)
├── .env.example           → Example: API URL for the browser
├── public/                → Static files (favicon, robots.txt)
│
└── src/
    ├── routes/            → ⭐ One file ≈ one page/screen
    │   ├── index.tsx          → Home page (“Give materials a second life”)
    │   ├── login.tsx          → Sign in
    │   ├── register.tsx       → Company registration
    │   ├── materials.index.tsx → Browse public listings
    │   ├── app.listings.new.tsx → Add surplus listing (after login)
    │   ├── app.requirements.tsx → Post what you need
    │   ├── app.matches.tsx      → View match results
    │   ├── app.requests.tsx     → Outgoing / incoming requests
    │   └── app.*.tsx            → Profile, projects, messages, admin, …
    │
    ├── components/
    │   ├── layout/        → Header, shell, logo (same frame on every page)
    │   ├── cards/         → Material cards on browse pages
    │   ├── common/        → Tables, loading states, shared buttons
    │   └── ui/            → Buttons, inputs, dialogs (design system)
    │
    ├── lib/
    │   ├── api.ts         → Talks to backend (HTTP requests)
    │   ├── auth.tsx       → Login state in the browser
    │   └── backend-map.ts → Converts form values to API format
    │
    └── styles.css         → Colours, fonts (ReBuild branding)
```

**For your report:** **`routes/`** = user journey screens; **`lib/api.ts`** = link between showroom and head office (`backend`).

---

### 7.5 Desktop folder (`desktop/`)

Simpler **Windows-style app** for lab demos (sign in → register surplus → search → your listings).

| File | What it does |
|------|----------------|
| `app.py` | Main window: login, tabs, forms, tables — **run this** with `python desktop/app.py` |
| `api_client.py` | Sends login and listing data to the backend over the network |
| `matching.py` | Local match scoring for the Search tab (works with listing data from server) |
| `material_types.py` | Dropdown list: brick, steel, frames, aggregate, units (nos, tonne, m³) |
| `backend_map.py` | Converts desktop form labels to the same format the API expects |
| `config.py` | Reads/writes `config.json` (server address, default localhost) |
| `config.example.json` | Sample config file |
| `theme.py` | Colours and fonts (ReBuild green / professional look) |
| `requirements.txt` | Extra Python packages for desktop (if any beyond standard library) |
| `README.md` | How to run desktop with backend + MongoDB |

**Note:** The sign-in screen **no longer shows** a “Backend connection” URL box. The app uses the default server address automatically (or `desktop/config.json` if your teammate edits it).

---

### 7.6 What you can skip as a civil student

| You can ignore (unless asked) | Why |
|-------------------------------|-----|
| `frontend/src/components/ui/*` (dozens of files) | Reusable button/input styling — not project logic |
| `frontend/bun.lock`, `node_modules/` | Machine-generated install files |
| `backend/.venv/` | Private Python toolbox folder on each PC |
| `__pycache__/` | Python temporary cache |
| Most `tests/` | Quality checks for programmers |

**Do understand:** problem statement, data fields, matching criteria, sustainability, and **which folder** holds matching (`backend/.../matching_service.py`) and user screens (`frontend/src/routes/` or `desktop/app.py`).

---

## 8. Software tools explained (pip, Python, and friends)

When your teammate runs commands, they use **tools**. Here is what they mean — no coding required to understand them.

### Python

**What:** A programming language used for `backend/`, `desktop/`, and `index.py`.  
**Analogy:** Like a **standard method statement** language the server understands.  
**On your PC:** Installed as `python` or `python3` (Windows: often `python` or `py`).

### pip

**What:** **P**ip **I**nstalls **P**ackages — Python’s **app store for libraries**.  
**Analogy:** Ordering **standard materials** (cement, steel) from an approved vendor list instead of making them from scratch.  
**Example:** `pip install -r requirements.txt` reads `requirements.txt` and downloads everything the backend needs (FastAPI, **uvicorn**, MongoDB driver, etc.).  
**Common error:** `No module named 'uvicorn'` means **pip was not run** (or wrong Python was used) — the library is missing.

### requirements.txt

**What:** A text **bill of materials** listing Python package names and versions.  
**Where:** `backend/requirements.txt`, `desktop/requirements.txt`.  
**Analogy:** BOQ line items: “1× FastAPI, 1× uvicorn, …”.

### Virtual environment (`.venv`)

**What:** A **private folder** on your laptop with its own pip packages, separate from other projects.  
**Analogy:** A **dedicated site store** for one project — tools don’t get mixed with another job.  
**Activate (Windows):** `.\.venv\Scripts\activate` — prompt shows `(.venv)`.  
**Activate (Mac/Linux):** `source .venv/bin/activate`.

### uvicorn

**What:** A small **engine** that runs the FastAPI server so it listens on `http://localhost:8000`.  
**Analogy:** **Power supply** for the site office — without it, `run.py` cannot serve the API.  
**Installed via:** `pip install -r requirements.txt` (listed in requirements).

### FastAPI

**What:** Framework used to build `backend/` — defines URLs like `/api/v1/materials`, login, matches.  
**Analogy:** **Pre-fabricated office module** with doors (endpoints) and inspection rules (validation).

### MongoDB

**What:** **Database** — stores users, companies, listings, requirements on disk.  
**Analogy:** **Central register + warehouse ledger** at head office.  
**Config:** `MONGODB_URL` in `backend/.env` (from `.env.example`).

### `.env` and `.env.example`

**What:** `.env.example` is a **template** (safe to share). `.env` is your **local copy** with real settings (often **not** uploaded to GitHub).  
**Analogy:** **Site configuration sheet** — database address, security keys — not your user login password.

### npm / bun / package.json

**What:** Tools to install **JavaScript** libraries for the **website** (`frontend/`).  
- **npm** — Node package manager (common).  
- **bun** — faster alternative; this repo may use either (`bun install` or `npm install`).  
**`package.json`:** Lists website dependencies and commands like `dev` (start local website).  
**Analogy:** pip, but for the **frontend showroom** instead of the Python server.

### React / Vite

**What:** **React** = library for building interactive pages. **Vite** = dev tool that serves the site quickly on port **5173**.  
**Analogy:** React = **modular prefab panels** for UI; Vite = **temporary site hut** for demos during construction.

### Git / GitHub

**What:** **Git** tracks changes to files; **GitHub** hosts the project online for the team.  
**Analogy:** **Revision register + cloud backup** for drawings and reports.

### JWT / API / localhost

| Term | Plain meaning |
|------|----------------|
| **API** | Server “menu” of actions (save listing, get matches) the apps call over the network |
| **localhost** | “This same computer” — `127.0.0.1` |
| **JWT** | Secure **pass token** after login, proving who you are on later requests |
| **HTTP** | Standard way browsers and apps send requests (like formal RFI letters) |

### Quick command cheat sheet (what teammates type)

| Command | Meaning in one line |
|---------|---------------------|
| `python -m venv .venv` | Create private Python toolbox folder |
| `.\.venv\Scripts\activate` | Turn on that toolbox (Windows) |
| `pip install -r requirements.txt` | Install all Python libraries listed |
| `python run.py` | Start backend server |
| `npm install` / `bun install` | Install website libraries |
| `npm run dev` / `bun run dev` | Start website locally |
| `python desktop/app.py` | Open desktop app window |

---

## 9. What data the system cares about (field checklist)

When explaining **surplus registration** to examiners, mention:

- Project / site name and **location**  
- **Material type** and **category**  
- **Quantity** and **unit** (critical for fair comparison)  
- **Condition** (reuse quality)  
- **Availability** (ready now, within 7 days, within 30 days, or a date)  
- **Price** or free material  

For **requirements**, add:

- Minimum acceptable **condition**  
- **Required date**  
- **Maximum distance** willing to transport  
- **Maximum budget** (optional)  

These mirror real decisions: IS codes and specs for quality, logistics cost vs distance, and programme dates.

---

## 10. Running the project (simple checklist for demo day)

If teammates handle coding, you should still know **what must be running**:

| Step | What | Why |
|------|------|-----|
| 1 | **MongoDB** running | Stores all listings and users |
| 2 | **Backend** (`backend/run.py`) | Accepts saves and computes matches |
| 3 | **Frontend** *or* **Desktop** | Lets users enter data |

**Windows (backend)** — from the `backend` folder:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

If you see **`No module named 'uvicorn'`**, Python has not installed the backend libraries yet — run `pip install -r requirements.txt` with the virtual environment **activated** (you should see `(.venv)` in the prompt).

**`.env` file** — copy of `.env.example` with settings like database address and secret keys. It is **configuration**, not your login password.

---

## 11. Sustainability & civil engineering angles (for reports)

Use these in your report, seminar, or viva:

1. **C&D waste volume** — Reuse reduces landfill and transport of virgin materials.  
2. **Embodied carbon** — Reusing steel, bricks, or timber avoids new production impacts.  
3. **Cost** — Surplus is often cheaper than market rate; platform improves **visibility**.  
4. **Logistics** — Distance and availability in the score reflect ** haul cost and programme**.  
5. **Quality** — Condition grades align with **inspection and acceptance** on reuse (similar spirit to visual grading on site).  
6. **Digital twin of yard inventory** — Listings act as a **reuse catalogue** across companies.

---

## 12. One-page summary for presentations

**Title:** ReBuild — Construction Material Exchange Platform  

**Aim:** Connect surplus C&D materials with projects that need them.  

**Method:** Web/desktop apps + central server; rule-based **matching score** (type, quantity, condition, location, time, budget).  

**Output:** Ranked matches, requests between companies, reduced waste.  

**Scope:** Multi-company platform with authentication; categories include masonry, steel, timber, fixtures, etc.  

**Limitation (honest):** Matching is **decision support**, not a replacement for site inspection, test certificates, or structural approval for critical elements.

---

## 13. Where to learn more in this repo

| If you want… | Open… |
|--------------|--------|
| Developer install steps | `README.md` |
| Desktop login and tabs | `desktop/README.md` |
| Simple scoring idea (terminal) | `index.py` |
| Full scoring rules | `backend/app/services/matching_service.py` |
| Public marketing flow (4 steps) | `frontend/src/routes/index.tsx` |

---

## 14. Questions examiners often ask (with short answers)

**Q: Is this only for bricks?**  
A: No — any listed category/type (steel, aggregate, frames, timber, etc.) with matching units.

**Q: Who decides the final deal?**  
A: The companies — the platform suggests matches; price and pickup are agreed between them.

**Q: Why MongoDB?**  
A: Flexible storage for many listings and companies; chosen by the development team for this API.

**Q: What is FastAPI / React?**  
A: Tools to build the **server** and **website** faster — like using standard formwork systems instead of carving wood from scratch.

**Q: What is pip and why do we run it?**  
A: Pip downloads the Python **libraries** the backend needs (including uvicorn). Without `pip install -r requirements.txt`, the server cannot start.

**Q: What was the mini project contribution?**  
A: Typically: problem definition, matching logic, desktop or CLI demo, and integration with a real database/API — your team’s report should state your exact division of work.

---

*This guide was written for civil engineering students presenting or maintaining the ReBuild mini project. For technical setup details, always follow `README.md`.*
