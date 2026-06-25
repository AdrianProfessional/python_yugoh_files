import requests
import random
import time

# ============================================
# YuGiOh Deck Generator — Python Script
# Stores deck as comma-separated card IDs
# in a Long Text field called "Card List"
# ============================================

API_KEY = "patniv0RRRddkos0B.5d09712d4ccf964c464c59eaef1efce09d7b6884192b067d7ea64259f335dbb3"
BASE_ID = "appY9amPlFG4Fnt6W"

CARDS_TABLE = "YuGiOh%20Cards"
DECKS_TABLE = "Decks"
DECK_SIZE = 30
STAPLES_ARCHETYPE = "Staples"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Curated list of fun archetypes to randomly pick from
ARCHETYPE_POOL = [
    "Blue-Eyes", "Dark Magician", "Red-Eyes", "Elemental HERO",
    "Destiny HERO", "Vision HERO", "Evil HERO", "Cyber Dragon",
    "Six Samurai", "Gladiator Beast", "Blackwing", "Lightsworn",
    "Infernity", "Gravekeepers", "Amazoness", "Madolche",
    "Ghostrick", "Chronomaly", "Bujin", "Satellarknight",
    "Burning Abyss", "Shaddoll", "Qliphort", "Nekroz",
    "Yosenju", "Kozmo", "Monarch", "Predaplant",
    "Zoodiac", "Subterror", "Invoked", "Altergeist",
    "Salamangreat", "Thunder Dragon", "Orcust", "Witchcrafter",
    "Endymion", "Eldlich", "Tri-Brigade", "Drytron",
    "Virtual World", "Floowandereeze", "Branded", "Springans",
    "Swordsoul", "Adventurer", "Tearlaments", "Spright",
    "Kashtira", "Purrely", "Snake-Eye", "Rescue-ACE"
]


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


def create_deck(deck_name, archetype, owner, card_ids, card_names):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{DECKS_TABLE}"
    payload = {
        "records": [{
            "fields": {
                "Deck Name": deck_name,
                "Archetype": archetype,
                "Owner": owner,
                "Card List": ",".join(card_ids)
            }
        }]
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code != 200:
        print(f"  Airtable error {response.status_code}: {response.text[:300]}")
        return False
    return True


def build_deck(archetype, archetype_map, staple_cards):
    ids = list(archetype_map.get(archetype, {}).keys())
    names = list(archetype_map.get(archetype, {}).values())

    combined = list(zip(ids, names))
    random.shuffle(combined)
    deck = combined[:DECK_SIZE]

    if len(deck) < DECK_SIZE:
        needed = DECK_SIZE - len(deck)
        print(f"  ⚡ Only {len(deck)} archetype cards — filling {needed} slots with staples.")
        staple_sample = random.sample(staple_cards, min(needed, len(staple_cards)))
        deck = deck + staple_sample

    deck_ids = [d[0] for d in deck]
    deck_names = [d[1] for d in deck]
    return deck_ids, deck_names


def main():
    print("📦 Loading all cards from Airtable...")
    all_cards = get_all_records(CARDS_TABLE, ["Name", "Archetype"])
    print(f"✅ Loaded {len(all_cards)} cards.")

    # Build archetype map: archetype -> {record_id: card_name}
    staple_cards = []  # list of (record_id, card_name)
    archetype_map = {}

    for card in all_cards:
        record_id = card["id"]
        fields = card.get("fields", {})
        arch = fields.get("Archetype", "")
        name = fields.get("Name", "")

        if arch == STAPLES_ARCHETYPE:
            staple_cards.append((record_id, name))
        elif arch:
            if arch not in archetype_map:
                archetype_map[arch] = {}
            archetype_map[arch][record_id] = name

    print(f"🎴 Found {len(archetype_map)} archetypes in database.")
    print(f"⭐ Found {len(staple_cards)} staple cards.")

    if not staple_cards:
        print("⚠️  No staple cards found — run tag_staples.py first.")
        return

    # Filter pool to only archetypes that exist in the database
    available = [a for a in ARCHETYPE_POOL if a in archetype_map]
    print(f"🎯 {len(available)} archetypes available from curated pool.")

    if len(available) < 2:
        print("⚠️  Not enough archetypes found — using random from full database instead.")
        available = list(archetype_map.keys())

    chosen = random.sample(available, 2)
    player_archetype = chosen[0]
    cpu_archetype = chosen[1]

    print(f"\n🎮 Player 1 archetype: {player_archetype}")
    print(f"🤖 CPU archetype:      {cpu_archetype}")

    for owner, archetype in [("Player 1", player_archetype), ("CPU", cpu_archetype)]:
        print(f"\n🔨 Building {owner}'s deck ({archetype})...")
        deck_ids, deck_names = build_deck(archetype, archetype_map, staple_cards)
        print(f"  ✅ Deck has {len(deck_ids)} cards.")
        print(f"  📋 Cards: {', '.join(deck_names[:5])}{'...' if len(deck_names) > 5 else ''}")

        deck_name = f"{owner} — {archetype}"
        if create_deck(deck_name, archetype, owner, deck_ids, deck_names):
            print(f"  🗂️  Deck record created: \"{deck_name}\"")
        else:
            print(f"  ❌ Failed to create deck for {owner}")

    print("\n✅ Both decks generated!")
    print("🚀 Ready to build the game interface!")


if __name__ == "__main__":
    main()
