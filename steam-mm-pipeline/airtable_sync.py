"""
airtable_sync.py — Sync parsed DEMO stats til Airtable

Flow:
1. Læs parsed match JSON
2. Transformér til Airtable Input Data schema
3. INSERT via Airtable API
4. Airtable formler beregner scores automatisk
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging
from pathlib import Path

from config import (
    AIRTABLE_PAT, AIRTABLE_BASE_ID, AIRTABLE_INPUT_TABLE,
    AIRTABLE_FIELD_MAP, LOG_LEVEL
)

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)


class AirtableSync:
    """Sync stats til Airtable"""

    BASE_URL = "https://api.airtable.com/v0"

    def __init__(self, pat: str, base_id: str):
        self.pat = pat
        self.base_id = base_id
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {pat}',
            'Content-Type': 'application/json',
        })

    def create_records(self, records: List[Dict]) -> bool:
        """
        Create records i Airtable

        Args:
            records: Liste af records (with 'fields' key)

        Returns:
            True hvis success
        """
        if not records:
            logger.warning("⚠️  Ingen records at create")
            return False

        url = f"{self.BASE_URL}/{self.base_id}/{AIRTABLE_INPUT_TABLE}"

        # Batch create (max 10 pr request)
        for batch_start in range(0, len(records), 10):
            batch = records[batch_start:batch_start + 10]

            payload = {'records': batch}

            try:
                logger.info(f"📤 Posting {len(batch)} records...")
                resp = self.session.post(url, json=payload, timeout=15)
                resp.raise_for_status()

                logger.info(f"✅ Created {len(batch)} records")

            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Airtable API fejl: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    logger.error(f"   Response: {e.response.text}")
                return False

        return True

    def get_existing_records(self, filters: Optional[str] = None) -> List[Dict]:
        """
        Hent eksisterende records (for dedup)

        Args:
            filters: Airtable filterByFormula (optional)

        Returns:
            Liste af records
        """
        url = f"{self.BASE_URL}/{self.base_id}/{AIRTABLE_INPUT_TABLE}"

        try:
            params = {}
            if filters:
                params['filterByFormula'] = filters

            resp = self.session.get(url, params=params, timeout=10)
            resp.raise_for_status()

            data = resp.json()
            return data.get('records', [])

        except Exception as e:
            logger.error(f"❌ Hent fejl: {e}")
            return []


def generate_fun_facts(player_name: str, current_stats: Dict, previous_records: List[Dict]) -> str:
    """
    Generer fun facts baseret på stats

    Insights: duos, improvers, peak performance, underdog stories
    """
    facts = []

    current_kd = current_stats.get('kills', 0) / (current_stats.get('deaths', 1) + 1)
    current_hs = current_stats.get('headshot_pct', 0)

    # Peak performance
    if current_stats.get('kills', 0) > 25:
        facts.append(f"🔥 Career-high territory: {current_stats['kills']} kills")

    # Headshot consistency
    if current_hs > 55:
        facts.append(f"💯 Precision player: {current_hs}% HS")

    # Progression trend
    if previous_records:
        recent_10 = previous_records[:10]
        prev_avg_kd = sum([r.get('fields', {}).get('Kills', 0) / (r.get('fields', {}).get('Death', 1) + 1) for r in recent_10]) / len(recent_10) if recent_10 else 0
        if current_kd > (prev_avg_kd + 0.5):
            facts.append(f"📈 On a roll: +{round(current_kd - prev_avg_kd, 1)} K/D vs avg")

    # Assist stats
    if current_stats.get('assists', 0) > 10:
        facts.append(f"🤝 Team player: {current_stats['assists']} assists")

    return " | ".join(facts) if facts else "Solid performance 👍"


def calculate_progression(steam_id: str, current_stats: Dict, previous_records: List[Dict]) -> Dict:
    """
    Beregn progression-data for spiller vs 10-game rolling average

    Args:
        steam_id: Player's Steam ID
        current_stats: Stats fra denne kamp
        previous_records: Tidligere records fra Airtable (sorteret by date, nyeste først)

    Returns:
        Dict med progression info
    """
    progression = {
        'kd_trend': None,
        'hs_trend': None,
        'momentum': None,
        'total_matches': len(previous_records) + 1,
    }

    if not previous_records:
        return progression

    # Bruge seneste 10 kampe for rolling average
    recent_matches = previous_records[:10] if len(previous_records) >= 10 else previous_records

    # Udtrk stats fra seneste kampe
    prev_kills = [r.get('fields', {}).get('Kills', 0) for r in recent_matches]
    prev_deaths = [r.get('fields', {}).get('Death', 1) for r in recent_matches]
    prev_hs = [r.get('fields', {}).get('HS%', 0) for r in recent_matches]

    # 10-game rolling averages
    avg_kills_10 = sum(prev_kills) / len(prev_kills) if prev_kills else 0
    avg_kd_10 = sum([k / (d + 1) for k, d in zip(prev_kills, prev_deaths)]) / len(prev_kills) if prev_kills else 0
    avg_hs_10 = sum(prev_hs) / len(prev_hs) if prev_hs else 0

    # Nuværende stats
    current_kills = current_stats.get('kills', 0)
    current_deaths = current_stats.get('deaths', 1)
    current_hs = current_stats.get('headshot_pct', 0)
    current_kd = current_kills / current_deaths if current_deaths > 0 else current_kills

    # Trends (current vs 10-game avg)
    progression['kd_trend'] = round(current_kd - avg_kd_10, 2)
    progression['hs_trend'] = round(current_hs - avg_hs_10, 1)

    # Momentum: compare seneste 3 vs tidligere 3
    if len(recent_matches) >= 6:
        recent_3_kd = sum([prev_kills[i] / (prev_deaths[i] + 1) for i in range(3)]) / 3
        earlier_3_kd = sum([prev_kills[i] / (prev_deaths[i] + 1) for i in range(3, 6)]) / 3
        momentum_direction = "📈" if recent_3_kd > earlier_3_kd else ("📉" if recent_3_kd < earlier_3_kd else "➡️")
    else:
        momentum_direction = "➡️"

    progression['momentum'] = momentum_direction

    return progression


def transform_parsed_to_airtable(parsed_match: Dict, match_date: str, progression_data: Dict = None) -> List[Dict]:
    """
    Transformér parsed DEMO stats til Airtable format

    Args:
        parsed_match: Output fra demo_parser
        match_date: Kampdato (ISO format)
        progression_data: Optional progression trends per player

    Returns:
        Liste af Airtable records (ready for insert)
    """
    players = parsed_match.get('players', {})
    map_name = parsed_match.get('map', 'unknown')
    results = []
    progression_data = progression_data or {}

    for steam_id, stats in players.items():
        # Map Python dict keys til Airtable field names
        fields = {}

        for airtable_field, python_key in AIRTABLE_FIELD_MAP.items():
            value = stats.get(python_key)

            # Type conversions
            if airtable_field == 'HS%':
                value = stats.get('headshot_pct', 0.0)
                if value:
                    value = value / 100.0  # Airtable bruger 0.xx format

            if airtable_field == 'DATO':
                value = match_date

            if airtable_field == 'Map':
                value = map_name

            # Skip hvis None/empty
            if value is not None and value != '':
                fields[airtable_field] = value

        # Sikr minimum felter
        if 'Spiller' not in fields:
            fields['Spiller'] = stats.get('player_name', f"Player_{steam_id[:8]}")

        if 'DATO' not in fields:
            fields['DATO'] = match_date

        if 'Map' not in fields:
            fields['Map'] = map_name

        # NOTE: Specialization og progression-data gemmes lokalt/i cache
        # Airtable-felter for disse skal oprettes først (FASE B)
        # Gemmes i stats for senere brugelse i dashboard

        record = {'fields': fields}
        results.append(record)

    return results


def sync_match_to_airtable(parsed_match: Dict, match_id: str) -> bool:
    """
    Main flow: Sync parsed match til Airtable

    Args:
        parsed_match: Output fra demo_parser
        match_id: For logging

    Returns:
        True hvis success
    """
    logger.info(f"\n{'─'*40}")
    logger.info(f"🔄 Syncing match {match_id} til Airtable...")

    # Beregn progression-data
    syncer = AirtableSync(AIRTABLE_PAT, AIRTABLE_BASE_ID)
    progression_data = {}

    players = parsed_match.get('players', {})
    for steam_id, stats in players.items():
        # Hent tidligere records for denne spiller
        filter_formula = f"{{Spiller}} = '{stats.get('player_name')}'"
        previous_records = syncer.get_existing_records(filters=filter_formula)
        progression = calculate_progression(steam_id, stats, previous_records)
        progression_data[steam_id] = progression

        if progression['total_matches'] > 1:
            logger.info(f"📈 {stats.get('player_name')}: {progression['total_matches']} kampe")

    # Transform data med progression
    match_date = datetime.now().isoformat().split('T')[0]  # YYYY-MM-DD
    airtable_records = transform_parsed_to_airtable(
        parsed_match,
        match_date,
        progression_data
    )

    if not airtable_records:
        logger.warning("⚠️  Ingen records at sync")
        return False

    logger.info(f"📊 {len(airtable_records)} player records ready")

    # Upload
    success = syncer.create_records(airtable_records)

    if success:
        logger.info(f"✅ Match synced!")
        # Log first player for verification
        if airtable_records:
            first = airtable_records[0]['fields']
            spiller = first.get('Spiller', 'Unknown')
            kills = first.get('Kills', 0)
            spec = first.get('Specialization', '—')
            logger.info(f"   Example: {spiller} — {kills} kills ({spec})")

    return success


def batch_sync_matches(parsed_matches: List[Dict]) -> Dict:
    """
    Sync multiple matches

    Returns:
        {'success': count, 'failed': count}
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"🎮 STEAM MM PIPELINE — Airtable Sync")
    logger.info(f"{'='*60}\n")

    success_count = 0
    failed_count = 0

    for idx, match in enumerate(parsed_matches, 1):
        match_id = f"match_{idx}"
        if sync_match_to_airtable(match, match_id):
            success_count += 1
        else:
            failed_count += 1

    logger.info(f"\n{'='*60}")
    logger.info(f"📊 RESULTATER:")
    logger.info(f"   ✅ Success: {success_count}")
    logger.info(f"   ❌ Failed: {failed_count}")
    logger.info(f"{'='*60}\n")

    return {
        'success': success_count,
        'failed': failed_count,
    }


if __name__ == '__main__':
    # Test: Sync en dummy match
    test_match = {
        'map': 'de_dust2',
        'duration_sec': 1800,
        'players': {
            '76561198123456789': {
                'player_name': 'TestPlayer1',
                'steam_id': '76561198123456789',
                'kills': 20,
                'deaths': 5,
                'assists': 5,
                'headshot_pct': 45.5,
                'adr': 85.2,
                'utility_damage': 120,
                'entry_frags': 5,
                'mvp_count': 3,
                'rounds_won': 10,
                'rounds_lost': 6,
                'total_rounds': 16,
                'knife_kills': 1,
                'knife_deaths': 0,
                'taser_kills': 0,
                'taser_deaths': 1,
                'pistol_kills': 3,
                'sniper_kills': 2,
                'multi_2k': 4,
                'multi_3k': 2,
                'multi_4k': 0,
                'multi_5k': 0,
            }
        }
    }

    logger.info("\n🧪 Testing Airtable sync with dummy data...\n")
    sync_match_to_airtable(test_match, 'test_match_001')
