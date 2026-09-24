#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_full_test.py — FULL PIPELINE TEST (simulator)

Kører hele pipeline uden rigtig DEMO:
1. Simulator DEMO parse
2. Upload til Airtable
3. Verify alt virker

Bruges når du ikke har .dem fil klar endnu
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from airtable_sync import batch_sync_matches
from datetime import datetime

print('\n' + '='*70)
print('[FULL PIPELINE TEST] Complete Workflow Simulation')
print('='*70 + '\n')

# Simulerer 3 forskellige kampe med forskellige stats
simulated_matches = [
    {
        'map': 'de_dust2',
        'duration_sec': 2400,
        'players': {
            '76561198111111111': {
                'player_name': 'Luffemann',
                'steam_id': '76561198111111111',
                'kills': 28,
                'deaths': 8,
                'assists': 12,
                'headshot_pct': 58.9,
                'adr': 105.3,
                'utility_damage': 210,
                'entry_frags': 12,
                'mvp_count': 6,
                'rounds_won': 16,
                'rounds_lost': 8,
                'total_rounds': 24,
                'knife_kills': 2,
                'knife_deaths': 0,
                'taser_kills': 1,
                'taser_deaths': 0,
                'pistol_kills': 5,
                'sniper_kills': 4,
                'multi_2k': 6,
                'multi_3k': 3,
                'multi_4k': 1,
                'multi_5k': 0,
            },
            '76561198222222222': {
                'player_name': 'Player2',
                'steam_id': '76561198222222222',
                'kills': 18,
                'deaths': 12,
                'assists': 10,
                'headshot_pct': 44.4,
                'adr': 72.1,
                'utility_damage': 180,
                'entry_frags': 5,
                'mvp_count': 2,
                'rounds_won': 16,
                'rounds_lost': 8,
                'total_rounds': 24,
                'knife_kills': 0,
                'knife_deaths': 1,
                'taser_kills': 0,
                'taser_deaths': 1,
                'pistol_kills': 2,
                'sniper_kills': 1,
                'multi_2k': 2,
                'multi_3k': 0,
                'multi_4k': 0,
                'multi_5k': 0,
            },
        }
    },
    {
        'map': 'de_mirage',
        'duration_sec': 1800,
        'players': {
            '76561198111111111': {
                'player_name': 'Luffemann',
                'steam_id': '76561198111111111',
                'kills': 22,
                'deaths': 6,
                'assists': 8,
                'headshot_pct': 50.0,
                'adr': 95.2,
                'utility_damage': 165,
                'entry_frags': 9,
                'mvp_count': 4,
                'rounds_won': 13,
                'rounds_lost': 3,
                'total_rounds': 16,
                'knife_kills': 1,
                'knife_deaths': 0,
                'taser_kills': 0,
                'taser_deaths': 0,
                'pistol_kills': 4,
                'sniper_kills': 2,
                'multi_2k': 5,
                'multi_3k': 1,
                'multi_4k': 0,
                'multi_5k': 0,
            },
            '76561198333333333': {
                'player_name': 'Player3',
                'steam_id': '76561198333333333',
                'kills': 15,
                'deaths': 9,
                'assists': 12,
                'headshot_pct': 33.3,
                'adr': 68.5,
                'utility_damage': 200,
                'entry_frags': 3,
                'mvp_count': 1,
                'rounds_won': 13,
                'rounds_lost': 3,
                'total_rounds': 16,
                'knife_kills': 0,
                'knife_deaths': 0,
                'taser_kills': 1,
                'taser_deaths': 0,
                'pistol_kills': 1,
                'sniper_kills': 0,
                'multi_2k': 1,
                'multi_3k': 0,
                'multi_4k': 0,
                'multi_5k': 0,
            },
        }
    },
    {
        'map': 'de_inferno',
        'duration_sec': 1950,
        'players': {
            '76561198111111111': {
                'player_name': 'Luffemann',
                'steam_id': '76561198111111111',
                'kills': 26,
                'deaths': 7,
                'assists': 6,
                'headshot_pct': 61.5,
                'adr': 98.7,
                'utility_damage': 195,
                'entry_frags': 10,
                'mvp_count': 5,
                'rounds_won': 14,
                'rounds_lost': 4,
                'total_rounds': 18,
                'knife_kills': 1,
                'knife_deaths': 0,
                'taser_kills': 0,
                'taser_deaths': 0,
                'pistol_kills': 3,
                'sniper_kills': 3,
                'multi_2k': 6,
                'multi_3k': 2,
                'multi_4k': 1,
                'multi_5k': 0,
            },
            '76561198444444444': {
                'player_name': 'Player4',
                'steam_id': '76561198444444444',
                'kills': 16,
                'deaths': 10,
                'assists': 9,
                'headshot_pct': 37.5,
                'adr': 71.3,
                'utility_damage': 175,
                'entry_frags': 4,
                'mvp_count': 1,
                'rounds_won': 14,
                'rounds_lost': 4,
                'total_rounds': 18,
                'knife_kills': 0,
                'knife_deaths': 0,
                'taser_kills': 0,
                'taser_deaths': 1,
                'pistol_kills': 2,
                'sniper_kills': 0,
                'multi_2k': 1,
                'multi_3k': 0,
                'multi_4k': 0,
                'multi_5k': 0,
            },
        }
    },
]

print('[INFO] Simulated Matches:\n')
for idx, match in enumerate(simulated_matches, 1):
    print(f'  Match {idx}: {match["map"].upper()} - {len(match["players"])} players')
    for steam_id, stats in match['players'].items():
        print(f'    - {stats["player_name"]}: {stats["kills"]} kills, {stats["deaths"]} deaths, {stats["headshot_pct"]:.1f}% HS')

print('\n' + '-'*70)
print('[UPLOAD] Syncing all matches to Airtable...\n')

results = batch_sync_matches(simulated_matches)

print('\n' + '='*70)
print('[COMPLETE] Full Pipeline Test Finished')
print('='*70)

if results['success'] > 0:
    print(f'\n[SUCCESS] {results["success"]} matches uploaded to Airtable!')
    print(f'\n[NEXT STEPS]:')
    print('  1. Open Airtable: LEO Tracker base')
    print('  2. Go to: Input Data table')
    print('  3. See: Your new stats records!')
    print(f'  4. Check: LeaderBoard is auto-updated')
    print(f'\n[VERIFY]:')
    print(f'  - Luffemann should have ~76 kills total')
    print(f'  - Multiple matches tracked')
    print(f'  - D-sync scores calculated')
    print(f'  - Rankings updated\n')
else:
    print(f'\n[ERROR] No matches uploaded (check Airtable credentials)\n')

if results['failed'] > 0:
    print(f'[WARNING] {results["failed"]} matches failed\n')
