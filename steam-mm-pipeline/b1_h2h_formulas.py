"""
B1: Head-to-Head Formulas Generator
Reads Input_Data, calculates H2H records per player pair, populates H2H table
"""

import os
import requests
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime

load_dotenv()

def determine_momentum(wins, losses):
    """Determine momentum status based on recent performance"""
    if wins + losses < 3:
        return "Early"

    # For simplicity, just compare wins to losses
    if wins > losses:
        return "Winning"
    elif losses > wins:
        return "Trailing"
    else:
        return "Even"

AIRTABLE_BASE_ID = "appZh8kPulBOY571R"
AIRTABLE_PAT = os.getenv("AIRTABLE_PAT")  # Use AIRTABLE_PAT, not AIRTABLE_API_KEY
AIRTABLE_BASE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}"

headers = {
    "Authorization": f"Bearer {AIRTABLE_PAT}",
    "Content-Type": "application/json",
}

# Fetch Input_Data
print("Fetching Input_Data...")
resp = requests.get(
    f"{AIRTABLE_BASE_URL}/Input%20Data",
    headers=headers
)
input_records = resp.json().get("records", [])
print(f"Found {len(input_records)} records\n")

# Group by date to find matchups
# Use K/D ratio for win/loss: K/D > 1 = win, K/D < 1 = loss
matches_by_date = defaultdict(list)
for rec in input_records:
    fields = rec.get("fields", {})
    player = fields.get("Spiller", "Unknown")
    date = fields.get("DATO", "Unknown")

    # Use K/D ratio to determine win/loss (since Kamp_Resultat always = 1)
    kills = fields.get("Kills", 0)
    deaths = fields.get("Death", 1)
    kd_ratio = kills / (deaths + 1)  # Avoid division by zero
    result = 1 if kd_ratio > 1.0 else (0 if kd_ratio < 1.0 else 0.5)  # 1=win, 0=loss, 0.5=neutral

    matches_by_date[date].append({
        "player": player,
        "result": result,
        "kd_ratio": kd_ratio,
        "record_id": rec.get("id")
    })

print("Matches grouped by date (K/D-based win/loss):")
for date, players in sorted(matches_by_date.items()):
    print(f"  {date}: {len(players)} players")
    for p in players[:3]:
        result_str = 'W' if p['result'] == 1 else ('L' if p['result'] == 0 else '=')
        print(f"    - {p['player']:20} K/D: {p['kd_ratio']:.2f} ({result_str})")
    if len(players) > 3:
        print(f"    ... and {len(players) - 3} more")

# Calculate H2H records
# Strategy: All players on same date are in SAME match
# Winners (result=1) vs Losers (result=0)
h2h_records = defaultdict(lambda: {"wins": 0, "losses": 0, "last_date": None})

print("\n\nCalculating H2H records...")
print("Strategy: For each date, pairwise matchups determined by highest K/D")

for date, players in matches_by_date.items():
    if len(players) < 2:
        continue

    print(f"\n  {date}: {len(players)} players")

    # Sort by K/D ratio descending to create pairwise matchups
    sorted_players = sorted(players, key=lambda p: p["kd_ratio"], reverse=True)

    # Create pairwise matchups: 1v2, 3v4, etc (tournament bracket style)
    for i in range(0, len(sorted_players) - 1, 2):
        p1 = sorted_players[i]
        p2 = sorted_players[i + 1]

        w_player = p1["player"]  # Higher K/D = winner
        l_player = p2["player"]
        w_kd = p1["kd_ratio"]
        l_kd = p2["kd_ratio"]

        # Create normalized pair key (sorted alphabetically)
        pair_key = tuple(sorted([w_player, l_player]))

        # Determine who is player1 and player2
        player1, player2 = pair_key

        # Update records - count win for player1 if they were winner
        if player1 == w_player:
            h2h_records[pair_key]["wins"] += 1
        else:
            h2h_records[pair_key]["losses"] += 1

        h2h_records[pair_key]["last_date"] = date

        print(f"    {w_player} (K/D {w_kd:.2f}) beat {l_player} (K/D {l_kd:.2f})")

# Display H2H results
print("\n\nH2H Records Summary:")
for (p1, p2), stats in sorted(h2h_records.items()):
    total = stats["wins"] + stats["losses"]
    print(f"  {p1} vs {p2}: {stats['wins']}-{stats['losses']} (Last: {stats['last_date']})")

# Fetch existing H2H records
print("\n\nFetching existing H2H records...")
h2h_resp = requests.get(
    f"{AIRTABLE_BASE_URL}/Head_to_Head",
    headers=headers
)
existing_h2h = {r["fields"].get("Matchup"): r["id"] for r in h2h_resp.json().get("records", [])}
print(f"Found {len(existing_h2h)} existing H2H records")

# Prepare records to create/update
records_to_create = []
records_to_update = []

for (player1, player2), stats in h2h_records.items():
    matchup_str = f"{player1} vs {player2}"

    record_data = {
        "fields": {
            "Matchup": matchup_str,
            "Player1": player1,
            "Player2": player2,
            "Wins_P1": stats["wins"],
            "Losses_P1": stats["losses"],
            "Total_Matches": stats["wins"] + stats["losses"],
            "Last_Match_Date": stats["last_date"],
            "Momentum": determine_momentum(stats["wins"], stats["losses"]),
        }
    }

    if matchup_str in existing_h2h:
        records_to_update.append({
            "id": existing_h2h[matchup_str],
            "fields": record_data["fields"]
        })
    else:
        records_to_create.append(record_data)

print(f"\nRecords to create: {len(records_to_create)}")
print(f"Records to update: {len(records_to_update)}")

# Create new records
if records_to_create:
    print("\nCreating new H2H records...")
    batch_size = 10
    for i in range(0, len(records_to_create), batch_size):
        batch = records_to_create[i:i+batch_size]
        resp = requests.post(
            f"{AIRTABLE_BASE_URL}/Head_to_Head",
            json={"records": batch},
            headers=headers
        )
        if resp.status_code == 200:
            print(f"  Created {len(batch)} records")
        else:
            print(f"  Error: {resp.status_code} - {resp.text}")

# Update existing records
if records_to_update:
    print("\nUpdating existing H2H records...")
    for record in records_to_update:
        resp = requests.patch(
            f"{AIRTABLE_BASE_URL}/Head_to_Head",
            json={"records": [record]},
            headers=headers
        )
        if resp.status_code == 200:
            print(f"  Updated {record['fields']['Matchup']}")
        else:
            print(f"  Error: {resp.status_code} - {resp.text}")

print("\n[DONE] B1 H2H Formulas Complete")
