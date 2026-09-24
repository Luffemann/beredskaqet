"""
steam_fetcher.py — Fetch CS2 match history fra Steam + download DEMOs

Flow:
1. Medlem logger ind med Steam ID
2. Fetch match history via Steam API
3. Find unprocessed matches
4. Download DEMO filer fra Steam
5. Return match metadata
"""

import requests
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import logging

from config import (
    STEAM_API_KEY, STEAM_APP_ID, DEMOS_DIR, STATS_CACHE,
    MATCH_HISTORY_COUNT, MIN_MATCH_DURATION_MIN, LOG_LEVEL
)

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

# Sikr demos folder
Path(DEMOS_DIR).mkdir(parents=True, exist_ok=True)


class SteamFetcher:
    """Henter CS2 match history + DEMOs fra Steam"""

    BASE_URL = "https://api.steampowered.com"

    def __init__(self, steam_api_key: str):
        self.api_key = steam_api_key
        self.session = requests.Session()
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        """Load processed matches cache"""
        if os.path.exists(STATS_CACHE):
            try:
                with open(STATS_CACHE, 'r') as f:
                    return json.load(f)
            except:
                return {'processed': []}
        return {'processed': []}

    def _save_cache(self):
        """Save processed matches cache"""
        with open(STATS_CACHE, 'w') as f:
            json.dump(self.cache, f, indent=2)

    def get_match_history(self, steam_id: str) -> Optional[List[Dict]]:
        """
        Hent CS2 match history for medlem

        Args:
            steam_id: Steam64 ID (e.g., '76561198123456789')

        Returns:
            Liste af matches med metadata
        """
        logger.info(f"Fetching match history for Steam ID: {steam_id}")

        try:
            # Endpoint: GetMatchHistoryByAccountID
            url = f"{self.BASE_URL}/ICSGOServersService/GetMatchHistoryByAccountID/v1/"

            params = {
                'key': self.api_key,
                'account_id': self._steam64_to_32(steam_id),
                'matches_requested': MATCH_HISTORY_COUNT,
            }

            resp = self.session.get(url, params=params, timeout=10)
            resp.raise_for_status()

            data = resp.json()
            matches = data.get('result', {}).get('matches', [])

            logger.info(f"✅ Fandt {len(matches)} matcher")
            return matches

        except Exception as e:
            logger.error(f"❌ Match history fejl: {e}")
            return None

    def download_demo(self, match_id: str, steam_id: str) -> Optional[str]:
        """
        Download DEMO fil fra Steam

        Args:
            match_id: Match ID fra history
            steam_id: Medlem's Steam ID

        Returns:
            Path til downloaded DEMO, eller None hvis fejl
        """
        # VIGTIGT: Steam giver ikke direkte DEMO download via API
        # DEMOs skal downloads via CSGO/CS2 game client eller
        # via tredje-part services som FACEIT, ESEA, osv.

        logger.warning(f"⚠️  Steam API giver IKKE DEMO download direkte")
        logger.warning(f"   Match ID: {match_id}")
        logger.warning(f"   Alternativer:")
        logger.warning(f"   1. Download manuelt fra Steam (Right-click match → Watch)")
        logger.warning(f"   2. Brug FACEIT/ESEA API hvis kamp spilles der")
        logger.warning(f"   3. Implement CS2 game client integration (komplekst)")

        return None

    def process_unprocessed_matches(self, steam_id: str) -> List[Dict]:
        """
        Hent og filtrer unprocessed matches

        Returns:
            Liste af nye matches som skal processeres
        """
        all_matches = self.get_match_history(steam_id)
        if not all_matches:
            return []

        # Filter: ignorer korte kampe, ignorer processerede
        new_matches = []
        for match in all_matches:
            match_id = match.get('match_id')
            duration_sec = match.get('duration', 0)
            duration_min = duration_sec / 60

            # Skip hvis for kort
            if duration_min < MIN_MATCH_DURATION_MIN:
                logger.debug(f"⏭️  Skipping kort match ({duration_min:.0f} min): {match_id}")
                continue

            # Skip hvis allerede processeret
            if match_id in self.cache['processed']:
                logger.debug(f"⏭️  Allerede processeret: {match_id}")
                continue

            new_matches.append({
                'match_id': match_id,
                'map': match.get('map_name', 'unknown'),
                'duration_sec': duration_sec,
                'timestamp': match.get('match_time', 0),
                'team1_score': match.get('team1_final_score', 0),
                'team2_score': match.get('team2_final_score', 0),
            })

        logger.info(f"📊 {len(new_matches)} nye matcher at processere")
        return new_matches

    def mark_processed(self, match_id: str):
        """Mark match som processeret"""
        if match_id not in self.cache['processed']:
            self.cache['processed'].append(match_id)
            self._save_cache()

    @staticmethod
    def _steam64_to_32(steam_id_64: str) -> int:
        """Konverter Steam64 ID til account ID (32-bit)"""
        return (int(steam_id_64) - 76561197960265728) >> 0


def fetch_and_prepare_matches(steam_id: str) -> List[Dict]:
    """
    Main flow: Fetch unprocessed matches

    Args:
        steam_id: Medlem's Steam ID (som de gav tilladelse til)

    Returns:
        Liste af matches ready for DEMO parsing
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"🎮 STEAM MM PIPELINE — Match Fetcher")
    logger.info(f"{'='*60}\n")

    fetcher = SteamFetcher(STEAM_API_KEY)

    # Hent og filtrer
    new_matches = fetcher.process_unprocessed_matches(steam_id)

    if not new_matches:
        logger.info("✅ Alle matcher allerede processeret")
        return []

    # Attempt download (vil fejle fordi Steam API giver det ikke)
    for match in new_matches:
        logger.info(f"\n📥 Processing: {match['map']} ({match['team1_score']}-{match['team2_score']})")
        match_id = match['match_id']

        # Denne vil returnere None — der kræves manuel download eller integration
        demo_path = fetcher.download_demo(match_id, steam_id)

        if demo_path:
            match['demo_path'] = demo_path
            fetcher.mark_processed(match_id)
        else:
            logger.warning(f"⚠️  Kunne ikke download DEMO for {match_id}")
            # VIGTIGT: Kan ikke markere som processeret uden DEMO!

    return new_matches


if __name__ == '__main__':
    # Test: Hent matches for test Steam ID
    TEST_STEAM_ID = '76561198000000000'  # Placeholder

    print(f"\n⚠️  BEMÆRK: Steam API giver IKKE DEMO download direkte")
    print(f"   Du skal enten:")
    print(f"   1. Download DEMOs manuelt fra Steam")
    print(f"   2. Placere .dem filer i '{DEMOS_DIR}' folder")
    print(f"   3. Parser vil så læse dem derfra\n")

    matches = fetch_and_prepare_matches(TEST_STEAM_ID)
    print(f"\n✅ Fandt {len(matches)} matcher (uden DEMOs)")
