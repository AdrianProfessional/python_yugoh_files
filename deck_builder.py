import requests
import random
import time
import json

API_KEY = "XXXXXXXXXXXXXXX"
BASE_ID = "XXXXXXXXXXXXXXXX"

CARDS_TABLE = "YuGiOh%20Cards"
DECKS_TABLE = "Decks"
DECK_SIZE = 30
STAPLES_ARCHETYPE = "Staples"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def get_all_records(table_name, fields):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{table_name}"
    records = []
    params = {"fields[]": fields}
    while True:
        response = requests.get(url, headers=HEADERS, params=params)
        data = response.json()
        if response.status_code != 200:
            print(f"Error fetching {table_name}: {data}")
            break
        records.extend(data.get("records", []))
        offset = data.get("offset")
        if offset:
            params["offset"] = offset
            time.sleep(0.25)
        else:
            break
    return records


def create_deck(deck_name, archetype, owner, card_record_ids):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{DECKS_TABLE}"

    # Build payload - use plain string IDs only
    linked = [{"id": str(rid)} for rid in card_record_ids]

    payload = {
        "records": [{
            "fields": {
                "Deck Name": deck_name,
                "Archetype": archetype,
                "Owner": owner,
                "Cards": linked
            }
        }]
    }

    # Print first 3 linked IDs to verify format
    print(f"  🔍 Payload sample: {json.dumps(linked[:3])}")

    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code != 200:
        print(f"  Airtable error {response.status_code}: {response.text[:500]}")
        return False
    return True


def main():
    print("📦 Loading all cards from Airtable...")
    all_cards = get_all_records(CARDS_TABLE, ["Name", "Archetype"])
    print(f"✅ Loaded {len(all_cards)} cards.")

    staple_cards = []
    archetype_map = {}

    for card in all_cards:
        record_id = card["id"]
        fields = card.get("fields", {})
        arch = fields.get("Archetype", "")
        if arch == STAPLES_ARCHETYPE:
            staple_cards.append(record_id)
        elif arch:
            if arch not in archetype_map:
                archetype_map[arch] = []
            archetype_map[arch].append(record_id)

    print(f"🎴 Found {len(archetype_map)} archetypes.")
    print(f"⭐ Found {len(staple_cards)} staple cards.")

    if not staple_cards:
        print("⚠️  No staple cards found — run tag_staples.py first.")
        return

    archetypes = list(archetype_map.keys())
    chosen = random.sample(archetypes, 2)
    player_archetype, cpu_archetype = chosen[0], chosen[1]

    print(f"\n🎮 Player 1 archetype: {player_archetype}")
    print(f"🤖 CPU archetype:      {cpu_archetype}")

    for owner, archetype in [("Player 1", player_archetype), ("CPU", cpu_archetype)]:
        print(f"\n🔨 Building {owner}'s deck ({archetype})...")

        ids = list(archetype_map.get(archetype, []))
        random.shuffle(ids)
        deck_ids = ids[:DECK_SIZE]

        if len(deck_ids) < DECK_SIZE:
            needed = DECK_SIZE - len(deck_ids)
            print(f"  ⚡ Only {len(deck_ids)} archetype cards — filling {needed} slots with staples.")
            shuffled_staples = random.sample(staple_cards, min(needed, len(staple_cards)))
            deck_ids = deck_ids + shuffled_staples

        # Ensure all IDs are plain strings
        deck_ids = [str(i) for i in deck_ids]
        print(f"  ✅ Deck has {len(deck_ids)} cards.")

        deck_name = f"{owner} — {archetype}"
        if create_deck(deck_name, archetype, owner, deck_ids):
            print(f"  🗂️  Deck created: \"{deck_name}\"")
        else:
            print(f"  ❌ Failed to create deck for {owner}")

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
