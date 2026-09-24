"""
demo_parser.py — Parse CS2 DEMO filer for player stats

Kræver: awpy (pip install awpy)
Fallback: Manual parsing hvis awpy ikke virker

Output: JSON med per-player stats
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

from config import DEMOS_DIR, PARSER_TYPE, LOG_LEVEL, AIRTABLE_FIELD_MAP

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

try:
    from awpy.demo import Demo
    AWPY_AVAILABLE = True
except ImportError:
    AWPY_AVAILABLE = False
    logger.warning("⚠️  awpy ikke tilgængelig. Install med: pip install awpy")


class DemoParser:
    """Parser CS2 DEMO filer"""

    def __init__(self, parser_type: str = 'awpy'):
        self.parser_type = parser_type
        if parser_type == 'awpy' and not AWPY_AVAILABLE:
            logger.error("❌ awpy ikke tilgængelig!")
            raise ImportError("Install awpy: pip install awpy")

    @staticmethod
    def classify_specialization(stats: Dict) -> str:
        """
        Klassificér spillers rolle baseret på stats

        Roller:
        - CARRY: High kills, high K/D, damage dealer
        - SUPPORT: High assists, high utility damage, team player
        - LURKER: Entry frags, selective deaths, economic awareness
        - IGL: Balanced, consistent, MVPs (harder without comms)
        """
        kills = stats['kills']
        assists = stats['assists']
        deaths = stats['deaths']
        utility_dmg = stats['utility_damage']
        entry_frags = stats['entry_frags']
        mvp = stats['mvp_count']

        kd_ratio = kills / (deaths + 1)

        # Scoring system
        carry_score = (kills * 1.5) + (kd_ratio * 10) - (assists * 0.5)
        support_score = (assists * 2) + (utility_dmg * 0.1) + (mvp * 5)
        lurker_score = (entry_frags * 3) + (kills * 0.5) - (deaths * 1.5)
        igl_score = (mvp * 10) + (assists * 1) + (kills * 0.5)

        scores = {
            'CARRY': carry_score,
            'SUPPORT': support_score,
            'LURKER': lurker_score,
            'IGL': igl_score,
        }

        return max(scores, key=scores.get)

    @staticmethod
    def detect_multikills(kills_in_round: List) -> int:
        """Detect multi-kill events (2k, 3k, 4k, 5k)"""
        # Simplified: count consecutive kills by same player in round
        # For full accuracy would need timestamp analysis
        return len(kills_in_round)

    def parse_demo(self, demo_path: str) -> Optional[Dict]:
        """
        Parse DEMO fil for stats

        Args:
            demo_path: Sti til .dem fil

        Returns:
            Dict med player stats, eller None hvis fejl
        """
        if not os.path.exists(demo_path):
            logger.error(f"❌ DEMO ikke fundet: {demo_path}")
            return None

        logger.info(f"📖 Parser DEMO: {Path(demo_path).name}")

        try:
            if self.parser_type == 'awpy':
                return self._parse_with_awpy(demo_path)
            else:
                logger.warning("⚠️  Parser type ikke implementeret")
                return self._parse_manual(demo_path)

        except Exception as e:
            logger.error(f"❌ Parse fejl: {e}")
            return None

    def _parse_with_awpy(self, demo_path: str) -> Dict:
        """
        Parse med awpy library

        awpy struktur:
        - demo.rounds[] → hver runde
        - round.kills[] → kills i runden
        - round.bomb_events[] → bomb events
        - round.players → player stats per runde
        """
        logger.info("🔧 Using awpy parser...")

        demo = Demo(demo_path)
        demo.parse()

        # Aggreger stats per player
        player_stats = {}
        player_round_kills = {}  # Track kills per round for multi-kill detection

        for player in demo.players:
            steam_id = str(player.steam_id) if player.steam_id else 'unknown'
            name = player.name or f"Player_{steam_id[:8]}"

            if steam_id not in player_stats:
                player_stats[steam_id] = {
                    'player_name': name,
                    'steam_id': steam_id,
                    'kills': 0,
                    'deaths': 0,
                    'assists': 0,
                    'headshot_count': 0,
                    'headshot_pct': 0.0,
                    'adr': 0.0,
                    'utility_damage': 0,
                    'entry_frags': 0,
                    'mvp_count': 0,
                    'rounds_won': 0,
                    'rounds_lost': 0,
                    'total_rounds': 0,
                    'knife_kills': 0,
                    'knife_deaths': 0,
                    'taser_kills': 0,
                    'taser_deaths': 0,
                    'multi_2k': 0,
                    'multi_3k': 0,
                    'multi_4k': 0,
                    'multi_5k': 0,
                    'pistol_kills': 0,
                    'sniper_kills': 0,
                    'total_damage': 0,
                    'specialization': 'UNKNOWN',
                }
                player_round_kills[steam_id] = {}

        # Parse hver runde
        for round_num, round_obj in enumerate(demo.rounds, 1):
            if not round_obj or not round_obj.kills:
                continue

            # Reset kills this round
            for steam_id in player_round_kills:
                player_round_kills[steam_id][round_num] = 0

            # Count rounds per player
            for player in demo.players:
                steam_id = str(player.steam_id) if player.steam_id else 'unknown'
                if steam_id not in player_stats:
                    continue

                player_stats[steam_id]['total_rounds'] += 1

                # Bestem hvis spiller vandt/tabte runden
                if round_obj.winner == player.team:
                    player_stats[steam_id]['rounds_won'] += 1
                else:
                    player_stats[steam_id]['rounds_lost'] += 1

            # Parse kills
            for kill in round_obj.kills:
                if not kill or not kill.attacker_steam_id:
                    continue

                attacker_id = str(kill.attacker_steam_id)
                victim_id = str(kill.victim_steam_id) if kill.victim_steam_id else None

                if attacker_id in player_stats:
                    player_stats[attacker_id]['kills'] += 1
                    player_round_kills[attacker_id][round_num] = player_round_kills[attacker_id].get(round_num, 0) + 1

                    # Weapon-specific kills
                    weapon = kill.weapon or 'unknown'
                    if 'knife' in weapon.lower():
                        player_stats[attacker_id]['knife_kills'] += 1
                    elif 'taser' in weapon.lower() or 'zeus' in weapon.lower():
                        player_stats[attacker_id]['taser_kills'] += 1
                    elif 'deagle' in weapon.lower() or 'awp' in weapon.lower():
                        player_stats[attacker_id]['sniper_kills'] += 1
                    elif 'usp' in weapon.lower() or 'glock' in weapon.lower() or 'p250' in weapon.lower():
                        player_stats[attacker_id]['pistol_kills'] += 1

                    # Headshot check
                    if kill.is_headshot:
                        player_stats[attacker_id]['headshot_count'] += 1

                if victim_id and victim_id in player_stats:
                    player_stats[victim_id]['deaths'] += 1

                    # Weapon-specific deaths
                    weapon = kill.weapon or 'unknown'
                    if 'knife' in weapon.lower():
                        player_stats[victim_id]['knife_deaths'] += 1
                    elif 'taser' in weapon.lower() or 'zeus' in weapon.lower():
                        player_stats[victim_id]['taser_deaths'] += 1

            # Parse assists
            if hasattr(round_obj, 'assists'):
                for assist in round_obj.assists or []:
                    if assist and assist.assister_steam_id:
                        assister_id = str(assist.assister_steam_id)
                        if assister_id in player_stats:
                            player_stats[assister_id]['assists'] += 1

            # Detect MVPs (hvis tilgængelig)
            if hasattr(round_obj, 'mvp_player_steam_id') and round_obj.mvp_player_steam_id:
                mvp_id = str(round_obj.mvp_player_steam_id)
                if mvp_id in player_stats:
                    player_stats[mvp_id]['mvp_count'] += 1

        # Detect multi-kills per player
        for steam_id, rounds in player_round_kills.items():
            for round_num, kill_count in rounds.items():
                if kill_count >= 2:
                    player_stats[steam_id]['multi_2k'] += 1
                if kill_count >= 3:
                    player_stats[steam_id]['multi_3k'] += 1
                if kill_count >= 4:
                    player_stats[steam_id]['multi_4k'] += 1
                if kill_count >= 5:
                    player_stats[steam_id]['multi_5k'] += 1

        # Calculate derived metrics
        for stats in player_stats.values():
            total_kills = stats['kills']
            total_rounds = stats['total_rounds'] or 1

            # Headshot %
            if total_kills > 0:
                stats['headshot_pct'] = round(
                    (stats['headshot_count'] / total_kills) * 100, 1
                )

            # ADR (Average Damage per Round)
            stats['adr'] = round(stats['total_damage'] / total_rounds, 1) if total_rounds else 0

            # Specialization classification
            stats['specialization'] = self.classify_specialization(stats)

        logger.info(f"✅ Parser færdig: {len(player_stats)} spillere")
        return {
            'map': getattr(demo, 'map_name', 'unknown'),
            'duration_sec': int(demo.header.playback_frames / 128),  # Approx
            'players': player_stats,
            'timestamp': demo.header.server_ordinal_number if hasattr(demo.header, 'server_ordinal_number') else 0,
        }

    def _parse_manual(self, demo_path: str) -> Dict:
        """
        Fallback: Manual parse (basic)

        VIGTIGT: Dette er placeholder. Rigtig DEMO parsing kræver:
        - Binary .dem file format knowledge
        - Event stream parsing
        - Protobuf deserialization (CS2 bruger protobuf)

        Anbefaling: Brug awpy eller wc-ez/cs2-demos (Node.js)
        """
        logger.warning("⚠️  Manual parser er placeholder — awpy anbefales!")

        return {
            'map': 'unknown',
            'duration_sec': 0,
            'players': {},
            'error': 'Manual parsing kræver awpy eller lignende library',
        }


def parse_all_demos() -> List[Dict]:
    """
    Parse alle ubehandlede DEMOs i demos/ folder

    Returns:
        Liste af parsed match data
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"🎮 STEAM MM PIPELINE — Demo Parser")
    logger.info(f"{'='*60}\n")

    if not os.path.exists(DEMOS_DIR):
        logger.error(f"❌ Demos folder ikke fundet: {DEMOS_DIR}")
        return []

    demo_files = list(Path(DEMOS_DIR).glob('*.dem'))

    if not demo_files:
        logger.warning(f"⚠️  Ingen .dem filer fundet i {DEMOS_DIR}")
        logger.info(f"   Instruktioner:")
        logger.info(f"   1. Download .dem filer fra Steam (højreklik på match → Watch)")
        logger.info(f"   2. Placér dem i: {DEMOS_DIR}")
        logger.info(f"   3. Kør dette script igen")
        return []

    logger.info(f"📂 Fandt {len(demo_files)} DEMO filer")

    parser = DemoParser(PARSER_TYPE)
    results = []

    for demo_path in demo_files:
        logger.info(f"\n{'─'*40}")
        parsed = parser.parse_demo(str(demo_path))

        if parsed and 'error' not in parsed:
            results.append(parsed)
            logger.info(f"✅ Successfull parsed")
        else:
            logger.error(f"❌ Parse fejlede")

    return results


if __name__ == '__main__':
    print("\n⚠️  VIGTIGT: awpy installation")
    print("   Kør først: pip install awpy\n")

    results = parse_all_demos()
    print(f"\n✅ Parsed {len(results)} matches")

    # Debug: Print første match
    if results:
        first = results[0]
        print(f"\nExample result:")
        print(f"  Map: {first.get('map')}")
        print(f"  Players: {len(first.get('players', {}))}")
