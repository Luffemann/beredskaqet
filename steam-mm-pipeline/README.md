# 🎮 Steam MM Pipeline — Valve Matchmaking → Airtable

Automatisk pipeline der konverterer CS2 Valve Matchmaking DEMO data direkte til Airtable statistikker.

## Oversigt

```
Steam Valve MM Kampe
        ↓
   Download DEMOs
        ↓
   Parse Stats (awpy)
        ↓
   Airtable Input Data
        ↓
   D-sync Scores (auto-calculate)
        ↓
   Leaderboard Updates
```

## Hvad du får

Efter hver kamp:
- ✅ Kill/Death/Assist stats per spiller
- ✅ Headshot %, ADR, Utility Damage
- ✅ Multi-kills (2k, 3k, 4k, 5k)
- ✅ Rounds Won/Lost
- ✅ Entry Frags, MVPs
- ✅ Automatic D-sync scoring
- ✅ Leaderboard rankings

## Setup

### 1. Install Python Dependencies

```bash
cd E:\danskeninjass2\steam-mm-pipeline
pip install -r requirements.txt
```

⚠️ **VIGTIGT:** `awpy` kræver C++ build tools
- Windows: Install [Visual C++ 14.0](https://visualstudio.microsoft.com/downloads/) eller højere
- Linux/Mac: `gcc` og `python-dev` (normalt allerede installeret)

### 2. Konfigurer Credentials

Rediger `config.py`:

```python
STEAM_API_KEY = 'AF64AE59BA8AADC6D4AD174F91727126'  # Allerede sat
AIRTABLE_PAT = '...'  # Allerede sat fra E:\.env
AIRTABLE_BASE_ID = 'appZh8kPulBOY571R'  # Allerede sat
```

## Brug

### Step 1: Download DEMO fra Steam

```
1. Åbn dine Completed Matches i Steam
2. Højreklik på CS2 match
3. Vælg "Watch" 
4. Vent ~ 30 minutter til DEMO er downloaded
5. Åbn file explorer → C:\Program Files (x86)\Steam\userdata\[USERID]\730\remote\
6. Kopier .dem fil til:
   E:\danskeninjass2\steam-mm-pipeline\demos\
```

### Step 2: Kør Pipeline

```bash
python main.py
```

Du bliver spurgt om dit Steam ID (17 cifre).

Pipeline kører:
- Henter match history fra Steam API
- Parser alle .dem filer i `demos/` folder
- Uploader stats til Airtable
- Leaderboard opdateres automatisk

### Step 3: Tjek Resultater

Åbn Airtable:
- **Input Data** tabel → nye player records
- **LeaderBoard** tabel → aggregerede scores
- **Scores opdateres automatisk** via formler

---

## KRITISK INFO: Steam API Begrænsninger

**Steam API kan IKKE downloade DEMOs direkte.**

Årsager:
- Valve giver ikke dette via OpenAPI
- DEMOs kræver game client eller manual download
- DEMOs lagres lokalt i Steams cache

**Løsninger:**
1. ✅ **Manual download** (anbefalet nu) — du downloader, pipeline parser
2. 🔜 **Automatisk** — kræver Steam game client integration (komplekst)
3. 🔜 **Alternative kilder** — FACEIT/ESEA API (hvis du spiller der)

---

## Fejlfinding

### Fejl: "awpy import error"

```bash
# Løsning:
pip install --upgrade setuptools wheel
pip install awpy
```

### Fejl: "No .dem files found"

1. Tjek at DEMOs er downloadet fra Steam
2. Tjek at de ligger i: `E:\danskeninjass2\steam-mm-pipeline\demos\`
3. Tjek filname ender med `.dem`

### Fejl: "401 Unauthorized" (Airtable)

1. Tjek at PAT token er gyldig i `config.py`
2. Tjek at base ID er korrekt
3. Genskab token i Airtable hvis nødvendigt

### Fejl: "Invalid Steam ID"

Steam ID skal være 17 cifre (Steam64 format):
- ❌ Forkert: `12345678` (8 cifre)
- ❌ Forkert: `STEAM_0:1:12345` (SteamID3 format)
- ✅ Rigtig: `76561198123456789` (17 cifre)

Find din Steam ID:
1. Åbn profil på Steam
2. URL: `https://steamcommunity.com/profiles/[STEAM_ID]`
3. Eller brug: https://steamidfinder.com/

### Fejl: "Demo parse fejlede"

1. Sikr at .dem fil er fra CS2, ikke CS:GO
2. Sikr at DEMO er fuldstændig downloadet
3. Prøv at genkøre `python main.py`

---

## Architecture

```
main.py (orchestrator)
├── steam_fetcher.py
│   └── fetch_and_prepare_matches()
│       ├── Get match history via Steam API
│       ├── Filter unprocessed matches
│       └── Attempt DEMO download (fails → manual)
│
├── demo_parser.py
│   └── parse_all_demos()
│       ├── Read .dem files from demos/ folder
│       ├── Parse with awpy library
│       ├── Extract player stats
│       └── Calculate metrics (K/D, HS%, ADR)
│
└── airtable_sync.py
    └── batch_sync_matches()
        ├── Transform to Airtable schema
        ├── POST to Input Data table
        └── Airtable formler beregner scores
```

## Data Flow

**Input til Airtable (per spiller per kamp):**

```json
{
  "Spiller": "PlayerName",
  "Kampe": 1,
  "Kills": 20,
  "Assist": 5,
  "Death": 8,
  "HS%": 0.45,
  "MVP": 3,
  "ADR": 85.2,
  "UD": 120,
  "EF": 5,
  "Vund._rund": 10,
  "Tabt_rund": 6,
  "Tot_rund": 16,
  "Map": "de_dust2",
  "DATO": "2026-09-23"
}
```

**Airtable beregner automatisk:**
- K/D Ratio
- Headshot %
- Impact Score
- Kamp_Score (D-sync)
- Leaderboard rank
- Performance tags

---

## Advanced: Automatisering

### Windows Scheduled Task

```powershell
# Kør hver dag kl 22:00 og check for nye DEMOs
# (Manuelt, eller brug Task Scheduler GUI)

$Action = New-ScheduledTaskAction -Execute 'python.exe' `
  -Argument 'E:\danskeninjass2\steam-mm-pipeline\main.py'

$Trigger = New-ScheduledTaskTrigger -Daily -At 22:00

Register-ScheduledTask -Action $Action -Trigger $Trigger `
  -TaskName "SteamMMPipeline" -Description "Auto-sync CS2 stats"
```

### Linux/Mac Cron

```bash
# Run every 2 hours
0 */2 * * * cd /path/to/steam-mm-pipeline && python main.py
```

---

## Testing

### Test med dummy data

```bash
# Sync test match uden rigtige DEMOs
python -c "
from airtable_sync import sync_match_to_airtable

test_match = {
    'map': 'de_dust2',
    'players': {
        '12345': {
            'player_name': 'TestPlayer',
            'kills': 20,
            'deaths': 5,
            # ... other stats
        }
    }
}

sync_match_to_airtable(test_match, 'test_001')
"
```

---

## Performance

- **Parse 1 DEMO:** ~ 5-10 sekunder (afhænger af DEMO længde)
- **Upload til Airtable:** ~ 1-2 sekunder per 10 records
- **Totalt for 1 match (5 spillere):** ~ 15-20 sekunder

---

## Licens & Credits

- **awpy** — [Bronze](https://github.com/LaihoE/awpy) (CS:GO/CS2 demo parser)
- **Airtable API** — Official
- **Steam API** — Limited (match history only, no DEMO download)

---

## Support

Hvis noget ikke virker:

1. **Læs fejlmeddelelsen** — Python siger typisk hvad der er galt
2. **Tjek logs** — Script printer detaljeret progress
3. **Verify setup** — Kør `python main.py` med ingen DEMOs først
4. **Isolate problem** — Test hver fase separat

---

**Status:** Beta 1.0
**Seneste update:** 2026-09-23
**Næste:** Automation + FACEIT integration
