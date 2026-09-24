# ⚡ Quick Start — 5 minutter

## Trin 1: Install Dependencies (2 min)

```bash
cd E:\danskeninjass2\steam-mm-pipeline
pip install -r requirements.txt
```

## Trin 2: Get Your Steam ID (1 min)

Din Steam ID er 17 cifre. Find den:
- Åbn Steam profil → URL indeholder `profiles/[ID]`
- Eller: https://steamidfinder.com/

**Eksempel:** `76561198123456789`

## Trin 3: Download 1 DEMO (manual)

1. Spil en CS2 match på Steam (Casual, Competitive, etc.)
2. Match slutter
3. Åbn Steam → Find match i "Completed Matches"
4. Højreklik → "Watch"
5. Vent 30 min til DEMO downloader
6. Find den i: `C:\Program Files (x86)\Steam\userdata\[ditt-nummer]\730\remote\`
7. Kopier .dem fil til: `E:\danskeninjass2\steam-mm-pipeline\demos\`

## Trin 4: Kør Pipeline (1 min)

```bash
cd E:\danskeninjass2\steam-mm-pipeline
python main.py
```

Enter din Steam ID når du bliver spurgt.

## Trin 5: Tjek Airtable (1 min)

Åbn [Airtable Base](https://airtable.com):
- Gå til "LEO Tracker" base
- Åbn "Input Data" tabel
- Se nye records med dine stats!

---

## ✅ Det virker hvis:

- ✅ Script starter uden fejl
- ✅ Parser finder .dem filer
- ✅ Airtable records created
- ✅ Scores beregnet automatisk

## ❌ Almindelige fejl:

| Fejl | Løsning |
|------|---------|
| "awpy not found" | `pip install awpy` |
| "No .dem files" | Tjek `demos/` folder |
| "401 Unauthorized" | Tjek credentials i `config.py` |
| "Invalid Steam ID" | Skal være 17 cifre |

---

## 🚀 Næste gange (automatisk):

1. Spil match
2. Download DEMO fra Steam
3. Placér i `demos/` folder
4. Kør `python main.py`
5. Stats i Airtable ✨

---

**Klar?** Start med `python main.py`!
