from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import requests
from functools import lru_cache
from datetime import datetime
import os
from dotenv import load_dotenv
from auth import create_access_token, verify_token, get_steam_profile, authenticate_demo

load_dotenv()

app = FastAPI(
    title="Beredskaqet Gaming API",
    description="Stats API for CS2 Steam MM Pipeline",
    version="1.0.0"
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config
AIRTABLE_BASE_ID = "appZh8kPulBOY571R"
AIRTABLE_PAT = os.getenv("AIRTABLE_API_KEY", "")
AIRTABLE_BASE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}"

# F1: Auth Models
class LoginRequest(BaseModel):
    steam_id: str

class LoginResponse(BaseModel):
    access_token: str
    player_name: str
    avatar: Optional[str] = None

class LogoutRequest(BaseModel):
    token: str

# Models
class PlayerStats(BaseModel):
    Spiller: str
    Kills: int
    Death: int
    Assist: int
    HS_pct: float
    ADR: float
    Map: str
    DATO: str

class LeaderboardEntry(BaseModel):
    Spiller: str
    kampe: int
    kills_total: int
    kd_ratio: float
    endelig_score: float

class ProgressionData(BaseModel):
    match_number: int
    kd_trend: float
    hs_trend: float
    momentum: str

# E1: Airtable API Wrapper with Cache
@lru_cache(maxsize=128)
def fetch_from_airtable(table_name: str, filter_formula: Optional[str] = None):
    """Fetch data from Airtable with caching"""
    headers = {
        "Authorization": f"Bearer {AIRTABLE_PAT}",
        "Content-Type": "application/json",
    }

    url = f"{AIRTABLE_BASE_URL}/{table_name}"
    params = {}
    if filter_formula:
        params["filterByFormula"] = filter_formula

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get("records", [])
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Airtable error: {str(e)}")

# E2: API Endpoints

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# F1: Steam Login Endpoint
@app.post("/api/auth/login")
async def login(request: LoginRequest) -> LoginResponse:
    """F1: Demo Steam login (returns JWT token)"""
    steam_id = request.steam_id
    from auth import DEMO_USERS

    # Demo mode: authenticate with mock users
    token = authenticate_demo(steam_id)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid Steam ID")

    # Fetch player name from demo users or Steam API
    player_name = DEMO_USERS.get(steam_id, "Player")
    profile = get_steam_profile(steam_id)
    if profile:
        player_name = profile["player_name"]

    return LoginResponse(
        access_token=token,
        player_name=player_name,
        avatar=profile["avatar"] if profile else None,
    )

# F2: Session validation
@app.post("/api/auth/verify")
async def verify(request: LoginRequest) -> dict:
    """F2: Verify JWT token"""
    token = request.steam_id  # Token passed as steam_id field (for simplicity)
    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token expired or invalid")

    return {
        "valid": True,
        "steam_id": payload.get("steam_id"),
        "player_name": payload.get("player_name"),
        "expires_at": payload.get("exp"),
    }

# F2: Logout
@app.post("/api/auth/logout")
async def logout(request: LogoutRequest) -> dict:
    """F2: Logout (invalidate token)"""
    from auth import logout_user
    logout_user(request.token)
    return {"status": "logged_out"}

@app.get("/api/player/{player_name}")
async def get_player_stats(player_name: str):
    """Get player's personal stats (E2: personal dashboard)"""
    records = fetch_from_airtable(
        "Input%20Data",
        filter_formula=f"{{Spiller}}='{player_name}'"
    )

    if not records:
        raise HTTPException(status_code=404, detail="Player not found")

    stats = [r["fields"] for r in records]
    return {
        "player_name": player_name,
        "total_matches": len(stats),
        "recent_matches": stats[:10],
        "avg_kills": sum(s.get("Kills", 0) for s in stats) / len(stats),
        "avg_kd": sum(s.get("Kills", 0) / (s.get("Death", 1) + 1) for s in stats) / len(stats),
    }

@app.get("/api/leaderboard")
async def get_leaderboard(limit: int = 50):
    """Get global leaderboard (E2: global rankings)"""
    records = fetch_from_airtable(
        "LeaderBoard",
        None
    )

    leaderboard = [
        {
            "rank": idx + 1,
            "player": r["fields"].get("Spiller"),
            "score": r["fields"].get("Endelig Score", 0),
            "matches": r["fields"].get("Antal kampe", 0),
        }
        for idx, r in enumerate(records[:limit])
    ]

    return {"leaderboard": leaderboard, "timestamp": datetime.now().isoformat()}

@app.get("/api/player/{player_name}/progression")
async def get_progression(player_name: str):
    """Get progression trends (E2: progression data)"""
    records = fetch_from_airtable(
        "Input%20Data",
        filter_formula=f"{{Spiller}}='{player_name}'"
    )

    if not records:
        raise HTTPException(status_code=404, detail="Player not found")

    stats = [r["fields"] for r in records]
    progression = [
        {
            "match": idx + 1,
            "kills": s.get("Kills", 0),
            "kd": s.get("Kills", 0) / (s.get("Death", 1) + 1),
            "hs_pct": s.get("HS%", 0),
            "adr": s.get("ADR", 0),
            "date": s.get("DATO", ""),
        }
        for idx, s in enumerate(stats)
    ]

    return {"progression": progression, "player": player_name}

@app.get("/api/player/{player_name}/h2h")
async def get_h2h(player_name: str):
    """Get head-to-head records (E2: H2H data)"""
    records = fetch_from_airtable(
        "Head_to_Head",
        filter_formula=f"{{Player1}}='{player_name}'"
    )

    h2h_data = [
        {
            "opponent": r["fields"].get("Player2"),
            "record": r["fields"].get("Record", "0-0"),
            "win_rate": r["fields"].get("Win_Rate_P1", 0),
        }
        for r in records
    ]

    return {"h2h": h2h_data, "player": player_name}

@app.get("/api/player/{player_name}/achievements")
async def get_achievements(player_name: str):
    """Get player achievements/badges (E2: badges)"""
    records = fetch_from_airtable(
        "Achievements",
        filter_formula=f"{{Player_Name}}='{player_name}'"
    )

    badges = [r["fields"].get("Badge_Type") for r in records]

    return {"badges": badges, "player": player_name, "total": len(badges)}

@app.get("/api/fun-facts")
async def get_fun_facts(limit: int = 10):
    """Get daily fun facts (E2: insights)"""
    records = fetch_from_airtable("Input%20Data", None)

    facts = [
        {
            "player": r["fields"].get("Spiller"),
            "fact": r["fields"].get("Fun_Facts", ""),
            "date": r["fields"].get("DATO", ""),
        }
        for r in records[:limit]
        if r["fields"].get("Fun_Facts")
    ]

    return {"fun_facts": facts}

# E3: WebSocket placeholder (for future real-time)
@app.get("/api/notifications/{player_name}")
async def get_notifications(player_name: str):
    """Get recent notifications (placeholder for WebSocket)"""
    return {
        "player": player_name,
        "notifications": [
            {"type": "badge_unlocked", "message": "You unlocked CARRY badge!", "date": datetime.now().isoformat()},
        ],
    }

# E4: Aggregation endpoints
@app.get("/api/stats/weekly")
async def get_weekly_stats():
    """Weekly stat summaries (E4)"""
    records = fetch_from_airtable("LeaderBoard", None)

    stats = [
        {
            "player": r["fields"].get("Spiller"),
            "score": r["fields"].get("Endelig Score", 0),
        }
        for r in records
    ]

    return {
        "period": "weekly",
        "stats": sorted(stats, key=lambda x: x["score"], reverse=True)[:20],
        "generated": datetime.now().isoformat(),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
