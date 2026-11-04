# ReBuild Desktop (Tkinter)

Desktop GUI for the **mini-project matching workflow**: register surplus C&D materials, search requirements, and view compatibility scores. Uses the same scoring logic as the root `index.py` CLI.

This is separate from the **web frontend** (`frontend/`) and **FastAPI backend** (`backend/`). It runs offline with in-memory data—ideal for demos and coursework that require Tkinter.

## Requirements

- Python **3.11+** with **Tk** (standard on Windows Python from python.org)
- No `pip install` needed for the desktop app

## Run (Windows)

```powershell
cd "C:\Users\VICTUS\Desktop\Mini Project\ReBuild-Construction-Material-Exchange-Platform"
python desktop\app.py
```

## Run (macOS / Linux)

```bash
cd ReBuild-Construction-Material-Exchange-Platform
python3 desktop/app.py
```

## Tabs

1. **Register surplus** — card-style form to add supplier listings  
2. **Search & match** — requirement form, color-coded results (green / amber / red by score)  
3. **All listings** — inventory table with refresh and clear  

The UI uses ReBuild brand colors (deep green header, leaf accent, light background).

## Full stack (optional)

For the production web app + API, use `backend/` and `frontend/` as described in the root [README](../README.md).
