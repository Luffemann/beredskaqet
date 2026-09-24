"""Steam OAuth & JWT Authentication Module"""

from datetime import datetime, timedelta
from typing import Optional
import jwt
import requests
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

# Config
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
STEAM_API_KEY = os.getenv("STEAM_API_KEY", "AF64AE59BA8AADC6D4AD174F91727126")

class TokenData:
    def __init__(self, steam_id: str, player_name: str):
        self.steam_id = steam_id
        self.player_name = player_name
        self.exp = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

def create_access_token(steam_id: str, player_name: str) -> str:
    """F2: Generate JWT token"""
    payload = {
        "steam_id": steam_id,
        "player_name": player_name,
        "exp": datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
        "iat": datetime.utcnow(),
    }
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@lru_cache(maxsize=100)
def get_steam_profile(steam_id: str) -> dict:
    """F3: Fetch Steam profile data"""
    url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    params = {
        "key": STEAM_API_KEY,
        "steamids": steam_id,
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("response", {}).get("players"):
            player = data["response"]["players"][0]
            return {
                "steam_id": player.get("steamid"),
                "player_name": player.get("personaname"),
                "avatar": player.get("avatarmedium"),
                "profile_url": player.get("profileurl"),
            }
        return None
    except Exception as e:
        print(f"Steam API error: {e}")
        return None

def logout_user(token: str) -> bool:
    """F2: Logout (invalidate token)"""
    # In production, add token to blacklist
    # For now, just return True (token expires naturally)
    return True

# Demo users for testing (F1: Mock Steam OpenID)
DEMO_USERS = {
    "76561198111111111": "Luffemann",
    "76561198222222222": "Player2",
    "76561198333333333": "Player3",
}

def authenticate_demo(steam_id: str) -> Optional[str]:
    """F1: Demo Steam OpenID login (for testing without app registration)"""
    if steam_id in DEMO_USERS:
        player_name = DEMO_USERS[steam_id]
        token = create_access_token(steam_id, player_name)
        return token
    return None
