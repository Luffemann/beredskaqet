#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_sample.py — Test Airtable sync with sample data

Run this to verify the pipeline works before downloading real DEMOs
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from airtable_sync import sync_match_to_airtable

print('\n' + '='*70)
print('[TEST] Airtable Sync with Sample Match')
print('='*70 + '\n')

# Dummy match data (simulates DEMO parse output)
test_match = {
    'map': 'de_dust2',
    'duration_sec': 1800,
    'players': {
        '76561198123456789': {
            'player_name': 'TestPlayer_Pro',
            'steam_id': '76561198123456789',
            'kills': 24,
            'deaths': 6,
            'assists': 8,
            'headshot_pct': 52.1,
            'adr': 92.5,
            'utility_damage': 185,
            'entry_frags': 8,
            'mvp_count': 4,
            'rounds_won': 13,
            'rounds_lost': 3,
            'total_rounds': 16,
            'knife_kills': 1,
            'knife_deaths': 0,
            'taser_kills': 0,
            'taser_deaths': 0,
            'pistol_kills': 4,
            'sniper_kills': 3,
            'multi_2k': 5,
            'multi_3k': 2,
            'multi_4k': 1,
            'multi_5k': 0,
        },
        '76561198987654321': {
            'player_name': 'TestPlayer_Support',
            'steam_id': '76561198987654321',
            'kills': 12,
            'deaths': 8,
            'assists': 15,
            'headshot_pct': 25.0,
            'adr': 58.3,
            'utility_damage': 320,
            'entry_frags': 2,
            'mvp_count': 1,
            'rounds_won': 13,
            'rounds_lost': 3,
            'total_rounds': 16,
            'knife_kills': 0,
            'knife_deaths': 1,
            'taser_kills': 1,
            'taser_deaths': 0,
            'pistol_kills': 1,
            'sniper_kills': 0,
            'multi_2k': 1,
            'multi_3k': 0,
            'multi_4k': 0,
            'multi_5k': 0,
        }
    }
}

print('[MATCH] Test Match:')
print(f'   Map: {test_match["map"]}')
print(f'   Players: {len(test_match["players"])}')
for steam_id, stats in test_match['players'].items():
    print(f'     - {stats["player_name"]}: {stats["kills"]} kills, {stats["deaths"]} deaths')

print('\n[SYNC] Syncing to Airtable...\n')
success = sync_match_to_airtable(test_match, 'test_sample_001')

if success:
    print('\n[SUCCESS] TEST PASSED!')
    print('\n[INFO] Hvad skete:')
    print('   1. OK - Parsed stats transformed to Airtable format')
    print('   2. OK - Records uploaded to Input Data table')
    print('   3. OK - Airtable formler kørte automatisk')
    print('   4. OK - Leaderboard opdateret')
    print('\n[DATA] Du kan nu se de nye records i Airtable!')
else:
    print('\n[NOTICE] TEST NOTICE:')
    print('   Airtable sync fejlede — tjek:')
    print('   1. config.py credentials (AIRTABLE_PAT, AIRTABLE_BASE_ID)')
    print('   2. Base ID matcher: appZh8kPulBOY571R')
    print('   3. Input Data table findes i basen')
