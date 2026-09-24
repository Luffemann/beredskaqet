"""
main.py — Steam MM Pipeline Orchestrator

Flow:
1. Fetch unprocessed matches fra Steam match history
2. Parse downloaded DEMOs
3. Sync results til Airtable
4. Auto-calculate scores via Airtable formler
"""

import sys
import logging
from pathlib import Path

from steam_fetcher import fetch_and_prepare_matches
from demo_parser import parse_all_demos
from airtable_sync import batch_sync_matches

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main pipeline"""

    print(f"\n{'='*70}")
    print(f"🎮 STEAM MM PIPELINE — Steam Valve MM → Airtable")
    print(f"{'='*70}\n")

    # ─── FASE 0: SETUP ───
    print("📋 SETUP CHECK:\n")

    try:
        import awpy
        print("✅ awpy installed (DEMO parser)")
    except ImportError:
        print("⚠️  awpy NOT installed")
        print("   Installer: pip install awpy")
        print("   awpy bruges til at parse .dem files\n")

    try:
        import requests
        print("✅ requests installed")
    except ImportError:
        print("❌ requests NOT installed")
        print("   Installer: pip install requests")
        sys.exit(1)

    try:
        from config import STEAM_API_KEY, AIRTABLE_PAT
        if not STEAM_API_KEY or not AIRTABLE_PAT:
            print("❌ Credentials mangler i config.py")
            sys.exit(1)
        print("✅ Steam API Key configured")
        print("✅ Airtable PAT configured\n")
    except Exception as e:
        print(f"❌ Config fejl: {e}")
        sys.exit(1)

    # ─── FASE 1: FETCH ───
    print("FASE 1️⃣  — FETCH Match History")
    print("─" * 70)
    print("\nInstruktion:")
    print("1. Du skal logger ind med din Steam ID")
    print("2. Systemet henter din match history fra Steam API")
    print("3. DEMOs skal downloades MANUELT fra Steam\n")

    steam_id_input = input("Enter your Steam ID (e.g., 76561198123456789): ").strip()

    if not steam_id_input or len(steam_id_input) != 17:
        print("❌ Invalid Steam ID")
        sys.exit(1)

    print(f"\n🔍 Fetching matches for {steam_id_input}...\n")
    matches = fetch_and_prepare_matches(steam_id_input)

    if not matches:
        print("\n⚠️  Ingen nye matches fundet eller ingen DEMOs tilgængelige")
        print("\nHvad skal du gøre:")
        print("1. Spil en CS2 match på Steam Valve Matchmaking")
        print("2. Efter kampen, højreklik på den i din match history")
        print("3. Vælg 'Watch' og vent til DEMO er downloaded")
        print("4. Kopier .dem fil til: E:\\danskeninjass2\\steam-mm-pipeline\\demos\\")
        print("5. Kør dette script igen\n")
        sys.exit(0)

    print(f"✅ Found {len(matches)} matches (with DEMOs needed)\n")

    # ─── FASE 2: PARSE ───
    print("\nFASE 2️⃣  — PARSE DEMO Files")
    print("─" * 70 + "\n")

    print("🔧 Parsing all .dem files in demos/ folder...\n")
    parsed_matches = parse_all_demos()

    if not parsed_matches:
        print("⚠️  Ingen DEMOs at parse")
        sys.exit(0)

    print(f"\n✅ Parsed {len(parsed_matches)} matches\n")

    # ─── FASE 3: SYNC ───
    print("\nFASE 3️⃣  — SYNC to Airtable")
    print("─" * 70 + "\n")

    print("📤 Uploading stats to Airtable...\n")
    results = batch_sync_matches(parsed_matches)

    # ─── SUMMARY ───
    print("\n" + "="*70)
    print("✅ PIPELINE COMPLETE")
    print("="*70)

    if results['success'] > 0:
        print(f"\n✅ {results['success']} matches synced to Airtable")
        print("\n📊 Hvad sker nu automatisk:")
        print("   1. Airtable beregner D-sync scores")
        print("   2. Leaderboard opdateres")
        print("   3. Player-historik gemmes")
        print("   4. Performance summaries genereres (AI)")
        print("\n🎯 Tjek Input Data tabellen i Airtable for nye records!\n")
    else:
        print(f"\n⚠️  Ingen matches blev synced (check logs for fejl)\n")

    if results['failed'] > 0:
        print(f"❌ {results['failed']} matches fejlede\n")

    # ─── NEXT STEPS ───
    print("📝 NÆSTE SKRIDT:\n")
    print("1. Spil mere CS2 på Steam Valve MM")
    print("2. Download DEMOs fra hver kamp")
    print("3. Placér .dem filer i: E:\\danskeninjass2\\steam-mm-pipeline\\demos\\")
    print("4. Kør main.py igen")
    print("\n💡 TIP: Du kan automatisere denne proces senere med scheduled tasks\n")

    print("="*70 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Pipeline cancelled")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Uventet fejl: {e}", exc_info=True)
        sys.exit(1)
