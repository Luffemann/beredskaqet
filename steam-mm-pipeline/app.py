"""
Beredskaqet Gaming API - Flask version (WSGI compatible for Namecheap)
"""

from flask import Flask, request, jsonify
from functools import lru_cache
from datetime import datetime
import requests
import os
from dotenv import load_dotenv
from auth import create_access_token, verify_token, get_steam_profile, authenticate_demo

load_dotenv()

app = Flask(__name__)

# Config
AIRTABLE_BASE_ID = "appZh8kPulBOY571R"
AIRTABLE_PAT = os.getenv("AIRTABLE_API_KEY", "")
AIRTABLE_BASE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}"

# CORS headers
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        return '', 200

# E1: Airtable API Wrapper with Cache
@lru_cache(maxsize=128)
def fetch_from_airtable(table_name: str, filter_formula=None):
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
        return []

# Health check (handle both /health and /api/health)
@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

# F1: Steam Login (handle both paths)
@app.route('/auth/login', methods=['POST'])
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    steam_id = data.get('steam_id')

    token = authenticate_demo(steam_id)
    if not token:
        return jsonify({"detail": "Invalid Steam ID"}), 401

    from auth import DEMO_USERS
    player_name = DEMO_USERS.get(steam_id, "Player")
    profile = get_steam_profile(steam_id)
    if profile:
        player_name = profile["player_name"]

    return jsonify({
        "access_token": token,
        "player_name": player_name,
        "avatar": profile["avatar"] if profile else None,
    })

# F2: Verify token
@app.route('/auth/verify', methods=['POST'])
@app.route('/api/auth/verify', methods=['POST'])
def verify():
    data = request.get_json()
    token = data.get('steam_id')
    payload = verify_token(token)

    if not payload:
        return jsonify({"detail": "Token expired or invalid"}), 401

    return jsonify({
        "valid": True,
        "steam_id": payload.get("steam_id"),
        "player_name": payload.get("player_name"),
        "expires_at": payload.get("exp"),
    })

# F2: Logout
@app.route('/auth/logout', methods=['POST'])
@app.route('/api/auth/logout', methods=['POST'])
def logout():
    from auth import logout_user
    data = request.get_json()
    logout_user(data.get('token', ''))
    return jsonify({"status": "logged_out"})

# Get player stats
@app.route('/player/<player_name>', methods=['GET'])
@app.route('/api/player/<player_name>', methods=['GET'])
def get_player_stats(player_name):
    records = fetch_from_airtable("Input%20Data", f"{{Spiller}}='{player_name}'")

    if not records:
        return jsonify({"detail": "Player not found"}), 404

    stats = [r["fields"] for r in records]
    return jsonify({
        "player_name": player_name,
        "total_matches": len(stats),
        "recent_matches": stats[:10],
        "avg_kills": sum(s.get("Kills", 0) for s in stats) / len(stats) if stats else 0,
        "avg_kd": sum(s.get("Kills", 0) / (s.get("Death", 1) + 1) for s in stats) / len(stats) if stats else 0,
    })

# Leaderboard
@app.route('/leaderboard', methods=['GET'])
@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    limit = request.args.get('limit', 50, type=int)
    records = fetch_from_airtable("LeaderBoard", None)

    leaderboard = [
        {
            "rank": idx + 1,
            "player": r["fields"].get("Spiller"),
            "score": r["fields"].get("Endelig Score", 0),
            "matches": r["fields"].get("Antal kampe", 0),
        }
        for idx, r in enumerate(records[:limit])
    ]

    return jsonify({"leaderboard": leaderboard, "timestamp": datetime.now().isoformat()})

# Progression
@app.route('/player/<player_name>/progression', methods=['GET'])
@app.route('/api/player/<player_name>/progression', methods=['GET'])
def get_progression(player_name):
    records = fetch_from_airtable("Input%20Data", f"{{Spiller}}='{player_name}'")

    if not records:
        return jsonify({"detail": "Player not found"}), 404

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

    return jsonify({"progression": progression, "player": player_name})

# Head-to-Head
@app.route('/player/<player_name>/h2h', methods=['GET'])
@app.route('/api/player/<player_name>/h2h', methods=['GET'])
def get_h2h(player_name):
    records = fetch_from_airtable("Head_to_Head", f"{{Player1}}='{player_name}'")

    h2h_data = [
        {
            "opponent": r["fields"].get("Player2"),
            "record": r["fields"].get("Record", "0-0"),
            "win_rate": r["fields"].get("Win_Rate_P1", 0),
        }
        for r in records
    ]

    return jsonify({"h2h": h2h_data, "player": player_name})

# Achievements
@app.route('/player/<player_name>/achievements', methods=['GET'])
@app.route('/api/player/<player_name>/achievements', methods=['GET'])
def get_achievements(player_name):
    records = fetch_from_airtable("Achievements", f"{{Player_Name}}='{player_name}'")

    badges = [r["fields"].get("Badge_Type") for r in records]

    return jsonify({"badges": badges, "player": player_name, "total": len(badges)})

# Fun facts
@app.route('/fun-facts', methods=['GET'])
@app.route('/api/fun-facts', methods=['GET'])
def get_fun_facts():
    limit = request.args.get('limit', 10, type=int)
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

    return jsonify({"fun_facts": facts})

# Notifications
@app.route('/notifications/<player_name>', methods=['GET'])
@app.route('/api/notifications/<player_name>', methods=['GET'])
def get_notifications(player_name):
    return jsonify({
        "player": player_name,
        "notifications": [
            {"type": "badge_unlocked", "message": "You unlocked CARRY badge!", "date": datetime.now().isoformat()},
        ],
    })

# Weekly stats
@app.route('/stats/weekly', methods=['GET'])
@app.route('/api/stats/weekly', methods=['GET'])
def get_weekly_stats():
    records = fetch_from_airtable("LeaderBoard", None)

    stats = [
        {
            "player": r["fields"].get("Spiller"),
            "score": r["fields"].get("Endelig Score", 0),
        }
        for r in records
    ]

    return jsonify({
        "period": "weekly",
        "stats": sorted(stats, key=lambda x: x["score"], reverse=True)[:20],
        "generated": datetime.now().isoformat(),
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
