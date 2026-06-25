import requests
import random
import time

# ============================================
# YuGiOh Deck Generator v2 — Bulk Mode
# Generates 25 Player 1 decks + 25 CPU decks
# ============================================

API_KEY = "patniv0RRRddkos0B.5d09712d4ccf964c464c59eaef1efce09d7b6884192b067d7ea64259f335dbb3"
BASE_ID = "appY9amPlFG4Fnt6W"

CARDS_TABLE = "YuGiOh%20Cards"
DECKS_TABLE = "Decks"
MAIN_DECK_SIZE = 30
EXTRA_DECK_SIZE = 15
STAPLES_ARCHETYPE = "Staples"
NUMBER_OF_DECKS = 25  # generates 25 Player 1 decks + 25 CPU decks = 50 total

EXTRA_DECK_TYPES = [
    "Fusion Monster", "Synchro Monster", "XYZ Monster",
    "Synchro Tuner Monster", "Synchro Pendulum Effect Monster",
    "XYZ Pendulum Effect Monster", "Pendulum Effect Fusion Monster",
    "Fusion Tuner Monster",
]

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
    "Swordsoul", "Tearlaments", "Spright", "Kashtira",
    "Purrely", "Snake-Eye", "Rescue-ACE", "Vanquish Soul",
]

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


def create_deck(deck_name, archetype, owner, card_ids, extra_card_ids):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{DECKS_TABLE}"
    payload = {
        "records": [{
            "fields": {
                "Deck Name": deck_name,
                "Archetype": archetype,
                "Owner": owner,
                "Card List": ",".join(card_ids),
                "Extra Card List": ",".join(extra_card_ids),
            }
        }]
    }
    while True:
        response = requests.post(url, headers=HEADERS, json=payload)
        if response.status_code == 429:
            print("  Rate limited — waiting 30s...")
            time.sleep(30)
            continue
        if response.status_code != 200:
            print(f"  Airtable error {response.status_code}: {response.text[:300]}")
            return False
        return True


def build_single_deck(archetype, owner, archetype_main, archetype_extra, staple_cards, deck_number):
    """Build one deck for a given archetype and owner."""

    # ── Main Deck ──────────────────────────────────────
    main_cards = list(archetype_main.get(archetype, []))
    random.shuffle(main_cards)
    deck = main_cards[:MAIN_DECK_SIZE]

    if len(deck) < MAIN_DECK_SIZE:
        needed = MAIN_DECK_SIZE - len(deck)
        shuffled_staples = random.sample(staple_cards, min(needed, len(staple_cards)))
        deck = deck + shuffled_staples

    # ── Extra Deck ─────────────────────────────────────
    extra_cards = list(archetype_extra.get(archetype, []))
    random.shuffle(extra_cards)
    extra_deck = extra_cards[:EXTRA_DECK_SIZE]

    main_ids = [c[0] for c in deck]
    extra_ids = [c[0] for c in extra_deck]
    deck_name = f"{owner} — {archetype} #{deck_number}"

    extra_info = f"+ {len(extra_deck)} extra" if extra_deck else "no extra deck"
    print(f"  {'🎮' if owner == 'Player 1' else '🤖'} {deck_name} ({len(deck)} main, {extra_info})")

    return deck_name, main_ids, extra_ids


def main():
    print("📦 Loading all cards from Airtable...")
    all_cards = get_all_records(CARDS_TABLE, ["Name", "Archetype", "Type"])
    print(f"✅ Loaded {len(all_cards)} cards.\n")

    # Bucket cards
    staple_cards = []
    archetype_main = {}
    archetype_extra = {}

    for card in all_cards:
        record_id = card["id"]
        fields = card.get("fields", {})
        arch = fields.get("Archetype", "")
        name = fields.get("Name", "")
        card_type = fields.get("Type", "")
        is_extra = card_type in EXTRA_DECK_TYPES

        if arch == STAPLES_ARCHETYPE:
            if not is_extra:
                staple_cards.append((record_id, name))
        elif arch:
            if is_extra:
                archetype_extra.setdefault(arch, []).append((record_id, name))
            else:
                archetype_main.setdefault(arch, []).append((record_id, name))

    print(f"🎴 {len(archetype_main)} archetypes with main deck cards")
    print(f"✨ {len(archetype_extra)} archetypes with extra deck cards")
    print(f"⭐ {len(staple_cards)} staple cards")

    if not staple_cards:
        print("\n⚠️  No staple cards found — run tag_staples.py first.")
        return

    # Filter to available archetypes
    available = [a for a in ARCHETYPE_POOL if a in archetype_main]
    print(f"🎯 {len(available)} archetypes available from curated pool\n")

    if len(available) < NUMBER_OF_DECKS:
        print(f"⚠️  Only {len(available)} archetypes available — using all of them.")
        # Pad with any remaining archetypes from the full database
        extras = [a for a in archetype_main.keys() if a not in available]
        random.shuffle(extras)
        available = available + extras

    # Pick NUMBER_OF_DECKS unique archetypes for Player 1
    # and NUMBER_OF_DECKS unique archetypes for CPU
    # (they can overlap — different owners can share archetypes)
    all_archetypes = list(set(available))
    random.shuffle(all_archetypes)

    player_archetypes = all_archetypes[:NUMBER_OF_DECKS]
    # Re-shuffle for CPU so they get different random selections
    random.shuffle(all_archetypes)
    cpu_archetypes = all_archetypes[:NUMBER_OF_DECKS]

    print(f"🏗️  Building {NUMBER_OF_DECKS} Player 1 decks + {NUMBER_OF_DECKS} CPU decks = {NUMBER_OF_DECKS * 2} total...\n")

    success = 0
    fail = 0

    for i, archetype in enumerate(player_archetypes, 1):
        deck_name, main_ids, extra_ids = build_single_deck(
            archetype, "Player 1", archetype_main, archetype_extra, staple_cards, i
        )
        if create_deck(deck_name, archetype, "Player 1", main_ids, extra_ids):
            success += 1
        else:
            fail += 1
        time.sleep(0.3)  # rate limit courtesy

    print()

    for i, archetype in enumerate(cpu_archetypes, 1):
        deck_name, main_ids, extra_ids = build_single_deck(
            archetype, "CPU", archetype_main, archetype_extra, staple_cards, i
        )
        if create_deck(deck_name, archetype, "CPU", main_ids, extra_ids):
            success += 1
        else:
            fail += 1
        time.sleep(0.3)

    print(f"\n{'='*50}")
    print(f"✅ Created {success} decks successfully")
    if fail:
        print(f"❌ {fail} decks failed")
    print(f"🚀 Ready to duel with {NUMBER_OF_DECKS} deck choices!")


if __name__ == "__main__":
    main()
