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

## 7. Folder map (what to say in a viva)

```text
ReBuild-Construction-Material-Exchange-Platform/
├── frontend/          → Web UI (React)
├── backend/           → API + matching + database logic (FastAPI + MongoDB)
├── desktop/           → Tkinter desktop client (connects to backend)
├── index.py           → Original CLI matching prototype
├── README.md          → Developer setup (install, run commands)
└── PROJECT_GUIDE_FOR_CIVIL_ENGINEERS.md  → This file
```

You **do not** need to memorize code inside these folders. For civil engineering focus, emphasize: **problem, data collected, matching criteria, sustainability, and user workflow**.

---

## 8. What data the system cares about (field checklist)

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

## 9. Running the project (simple checklist for demo day)

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

## 10. Sustainability & civil engineering angles (for reports)

Use these in your report, seminar, or viva:

1. **C&D waste volume** — Reuse reduces landfill and transport of virgin materials.  
2. **Embodied carbon** — Reusing steel, bricks, or timber avoids new production impacts.  
3. **Cost** — Surplus is often cheaper than market rate; platform improves **visibility**.  
4. **Logistics** — Distance and availability in the score reflect ** haul cost and programme**.  
5. **Quality** — Condition grades align with **inspection and acceptance** on reuse (similar spirit to visual grading on site).  
6. **Digital twin of yard inventory** — Listings act as a **reuse catalogue** across companies.

---

## 11. One-page summary for presentations

**Title:** ReBuild — Construction Material Exchange Platform  

**Aim:** Connect surplus C&D materials with projects that need them.  

**Method:** Web/desktop apps + central server; rule-based **matching score** (type, quantity, condition, location, time, budget).  

**Output:** Ranked matches, requests between companies, reduced waste.  

**Scope:** Multi-company platform with authentication; categories include masonry, steel, timber, fixtures, etc.  

**Limitation (honest):** Matching is **decision support**, not a replacement for site inspection, test certificates, or structural approval for critical elements.

---

## 12. Where to learn more in this repo

| If you want… | Open… |
|--------------|--------|
| Developer install steps | `README.md` |
| Desktop login and tabs | `desktop/README.md` |
| Simple scoring idea (terminal) | `index.py` |
| Full scoring rules | `backend/app/services/matching_service.py` |
| Public marketing flow (4 steps) | `frontend/src/routes/index.tsx` |

---

## 13. Questions examiners often ask (with short answers)

**Q: Is this only for bricks?**  
A: No — any listed category/type (steel, aggregate, frames, timber, etc.) with matching units.

**Q: Who decides the final deal?**  
A: The companies — the platform suggests matches; price and pickup are agreed between them.

**Q: Why MongoDB?**  
A: Flexible storage for many listings and companies; chosen by the development team for this API.

**Q: What is FastAPI / React?**  
A: Tools to build the **server** and **website** faster — like using standard formwork systems instead of carving wood from scratch.

**Q: What was the mini project contribution?**  
A: Typically: problem definition, matching logic, desktop or CLI demo, and integration with a real database/API — your team’s report should state your exact division of work.

---

*This guide was written for civil engineering students presenting or maintaining the ReBuild mini project. For technical setup details, always follow `README.md`.*
