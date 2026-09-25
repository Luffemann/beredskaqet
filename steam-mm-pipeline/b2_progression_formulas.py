"""
B2: Progression Dashboard Formulas
Reads Input_Data, calculates progression metrics, populates Progression table
"""

import os
import requests
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

AIRTABLE_BASE_ID = "appZh8kPulBOY571R"
AIRTABLE_PAT = os.getenv("AIRTABLE_PAT")
AIRTABLE_BASE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}"

headers = {
    "Authorization": f"Bearer {AIRTABLE_PAT}",
    "Content-Type": "application/json",
}

print("="*60)
print("B2: PROGRESSION DASHBOARD FORMULAS")
print("="*60 + "\n")

# Fetch Input_Data
print("Fetching Input_Data...")
resp = requests.get(
    f"{AIRTABLE_BASE_URL}/Input%20Data",
    headers=headers
)
input_records = resp.json().get("records", [])
print(f"Found {len(input_records)} records\n")

# Group by player and sort by date
player_matches = defaultdict(list)
for rec in input_records:
    fields = rec.get("fields", {})
    player = fields.get("Spiller", "Unknown")
    date = fields.get("DATO", "Unknown")
    kills = fields.get("Kills", 0)
    deaths = fields.get("Death", 0)
    hs_percent = fields.get("HS%", 0)

    player_matches[player].append({
        "date": date,
        "kills": kills,
        "deaths": deaths,
        "hs_percent": hs_percent,
        "record_id": rec.get("id")
    })

print(f"Players found: {len(player_matches)}\n")

# Calculate progression data for each player
progression_records = []

for player, matches in sorted(player_matches.items()):
    # Sort matches by date
    sorted_matches = sorted(matches, key=lambda x: x["date"])

    print(f"  {player}: {len(sorted_matches)} matches")

    cumulative_kills = 0
    cumulative_deaths = 0

    for match_num, match in enumerate(sorted_matches, 1):
        cumulative_kills += match["kills"]
        cumulative_deaths += match["deaths"]

        kd_ratio = match["kills"] / (match["deaths"] + 1)

        # Milestone detection
        milestones = []
        if cumulative_kills >= 100:
            milestones.append("100_Kills")
        if match["hs_percent"] >= 0.60:
            milestones.append("60_HS_Percent")
        if kd_ratio >= 3.0:
            milestones.append("3.0_KD_Ratio")

        record = {
            "fields": {
                "Player_Name": player,
                "Match_Number": match_num,
                "Kills": match["kills"],
                "Deaths": match["deaths"],
                "K/D_Ratio": round(kd_ratio, 2),
                "HS_Percent": round(match["hs_percent"] * 100, 1),
                "Date": match["date"],
            }
        }

        if milestones:
            record["fields"]["Milestone"] = milestones[0]  # Single select - pick first

        progression_records.append(record)

print(f"\nTotal progression records to create: {len(progression_records)}\n")

# Create records in Progression table
print("Creating progression records in Airtable...")
batch_size = 10

for i in range(0, len(progression_records), batch_size):
    batch = progression_records[i:i+batch_size]
    resp = requests.post(
        f"{AIRTABLE_BASE_URL}/Progression",
        json={"records": batch},
        headers=headers
    )

    if resp.status_code == 200:
        created = resp.json().get("records", [])
        print(f"  Batch {i//batch_size + 1}: Created {len(created)} records")
    else:
        print(f"  Error: {resp.status_code} - {resp.text[:200]}")

print("\n" + "="*60)
print("[DONE] B2 Progression Formulas Complete")
print("="*60)

# Verify
print("\nVerification - Sample progression records:")
resp = requests.get(
    f"{AIRTABLE_BASE_URL}/Progression?maxRecords=5",
    headers=headers
)
records = resp.json().get("records", [])
for rec in records:
    fields = rec.get("fields", {})
    print(f"  {fields.get('Player_Name', 'N/A'):20} Match {fields.get('Match_Number', 0):2}: " +
          f"K/D {fields.get('K/D_Ratio', 0):.2f} | HS% {fields.get('HS_Percent', 0):.1f}%")
