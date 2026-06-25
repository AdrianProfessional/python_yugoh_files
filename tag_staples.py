import requests
import time

# ============================================
# YuGiOh Staples Tagger — Python Script
# ============================================

API_KEY = "patniv0RRRddkos0B.5d09712d4ccf964c464c59eaef1efce09d7b6884192b067d7ea64259f335dbb3"
BASE_ID = "appY9amPlFG4Fnt6W"
CARDS_TABLE = "YuGiOh%20Cards"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Full staples list
STAPLES = [
    # Link 1
    "Gravity Controller", "Linguriboh", "Link Spider", "Relinquished Anima",
    "Salamangreat Almiraj", "Secure Gardna",
    # Link 2
    "Barricadeborg Blocker", "Cross-Sheep", "Dharc the Dark Charmer, Gloomy",
    "Donner, Dagger Fur Hire", "Hiita the Fire Charmer, Ablaze", "I:P Masquerena",
    "Knightmare Cerberus", "Knightmare Phoenix", "Lyna the Light Charmer, Lustrous",
    "Muckraker From the Underworld", "Pitknight Earlie", "Salamangreat Sunlight Wolf",
    "Splash Mage", "S:P Little Knight", "Unchained Soul Lord of Yama",
    # Link 3
    "Black Luster Soldier - Soldier of Chaos", "Decode Talker Heatsoul",
    "Hraesvelgr, the Desperate Doom Eagle", "Knightmare Unicorn",
    "Promethean Princess, Bestower of Flames", "Selene, Queen of the Master Magicians",
    "Topologic Trisbaena", "Unchained Soul of Anguish",
    # Link 4
    "Accesscode Talker", "Amphibious Swarmship Amblowhale", "Borrelsword Dragon",
    "Borreload Dragon", "Knightmare Gryphon", "Mekk-Knight Crusadia Avramax",
    "Salamangreat Raging Phoenix", "Saryuja Skull Dread", "Topologic Bomber Dragon",
    "Topologic Zeroboros", "Unchained Abomination", "Worldsea Dragon Zealantis",
    # Link 5
    "Underworld Goddess of the Closed World",
    # Xyz Flexible
    "Divine Arsenal AA-ZEUS - Sky Thunder", "Dark Armed, the Dragon of Annihilation",
    "Downerd Magician", "Number F0: Utopic Future", "Number F0: Utopic Draco Future",
    "Super Starslayer TY-PHON - Sky Crisis",
    # Xyz Rank 1
    "Kikinagashi Fucho", "Lyrilusc - Assembled Nightingale",
    # Xyz Rank 2
    "Number 29: Mannequin Cat", "Onibimaru Soul Sweeper", "Toadally Awesome",
    # Xyz Rank 3
    "The Phantom Knights of Break Sword",
    # Xyz Rank 4
    "Abyss Dweller", "Evilswarm Exciton Knight", "Evilswarm Nightmare",
    "Gagaga Cowboy", "Gallant Granite", "Infernal Flame Banshee",
    "Number 60: Dugares the Timeless", "Number 41: Bagooska the Terribly Tired Tapir",
    "Raider's Knight", "Time Thief Redoer", "Tornado Dragon",
    # Xyz Rank 5
    "Arc Rebellion Xyz Dragon",
    # Xyz Rank 6
    "Evolzar Lars", "Wollow, Founder of the Drudge Dragons",
    # Xyz Rank 7
    "Number 11: Big Eye", "Number 76: Harmonizer Gradielle",
    # Xyz Rank 8
    "Coach King Giantrainer", "Number 38: Hope Harbinger Dragon Titanic Galaxy",
    "Number 68: Sanaphond the Sky Prison", "Number 90: Galaxy-Eyes Photon Lord",
    "Number 97: Draglubion", "The Zombie Vampire",
    # Xyz Rank 9
    "Mereologic Aggregator",
    # Fusion
    "Berfomet the Mythical King of Phantom Beasts", "Chimera the King of Phantom Beasts",
    "Elder Entity N'tss", "Guardian Chimera", "Earth Golem @Ignister",
    "Garura, Wings of Resonant Life", "Starving Venom Fusion Dragon",
    "Predaplant Dragostapelia", "Mudragon of the Swamp", "Millennium-Eyes Restrict",
    # Synchro
    "Accel Synchro Stardust Dragon", "Bystial Dis Pater", "Chaos Angel",
    "Coral Dragon", "Crimson Dragon", "Enigmaster Packbit", "F.A. Dawn Dragster",
    "Formula Synchron", "Herald of the Arc Light", "Golden Cloud Beast - Malong",
    "PSY-Framelord Omega", "Tri-Edge Master",
    # Floodgates
    "Artifact Lancea", "Different Dimension Ground", "Dimensional Barrier",
    "Dimension Shifter", "Droll & Lock Bird", "Mistaken Arrest",
    "Anti-Spell Fragrance", "Deck Lockdown", "Denko Sekka",
    "Grave of the Super Ancient Organism", "Gozen Match", "Inspector Boarder",
    "Necrovalley", "Rivalry of Warlords", "Secret Village of the Spellcasters",
    "Skill Drain", "There Can Be Only One", "Vanity's Fiend",
    # Hand Traps / Negation
    "Ash Blossom & Joyous Spring", "Bystial Magnamhut", "Bystial Druiswurm",
    "D.D. Crow", "Effect Veiler", "Ghost Ogre & Snow Rabbit",
    "Ghost Belle & Haunted Mansion", "Ghost Mourner & Moonlit Chill",
    "Infinite Impermanence", "Mulcharmy Purulia", "Nibiru, the Primal Being",
    "PSY-Framegear Delta", "PSY-Framegear Gamma", "Retaliating \"C\"",
    "Skull Meister", "Book of Eclipse", "Book of Moon", "Crossout Designator",
    "Called by the Grave", "Dark Ruler No More", "Forbidden Droplet",
    "Forbidden Chalice", "Destructive Daruma Karma Cannon", "Ice Dragon's Prison",
    "Lost Wind", "Solemn Judgment", "Solemn Strike", "The Black Goat Laughs",
    # Removal
    "Kurikara Divincarnate", "The Winged Dragon of Ra - Sphere Mode",
    "Gameciel, the Sea Turtle Kaiju", "Gadarla, the Mystery Dust Kaiju",
    "Jizukiru, the Star Destroying Kaiju", "Radian, the Multidimensional Kaiju",
    "Lava Golem", "Santa Claws", "Enemy Controller", "Super Polymerization",
    "Change of Heart", "Dark Hole", "Mind Control", "Raigeki", "Snatch Steal",
    "Herald of the Abyss", "Ultimate Slayer", "Crackdown",
    "Harpie's Feather Duster", "Twin Twisters", "Cosmic Cyclone", "Galaxy Cyclone",
    "Eradicator Epidemic Virus", "Dinowrestler Pankratops", "Evenly Matched",
    "Kashtira Fenrir", "Lightning Storm",
    # Draw Power
    "Allure of Darkness", "Card Destruction", "Card of Demise",
    "Fantastical Dragon Phantazmay", "Pot of Desires", "Pot of Duality",
    "Pot of Extravagance", "Pot of Prosperity", "Trade-In", "Upstart Goblin",
    # Other Monsters
    "Absolute King Back Jack", "Danger!? Jackalope?", "Danger! Nessie!",
    "Danger!? Tsuchinoko?", "Danger! Mothman!", "Danger! Bigfoot!",
    "Gizmek Orochi, the Serpentron Sky Slasher", "Parallel eXceed",
    "Volcanic Scattershot",
    # Other Spells
    "Foolish Burial", "Foolish Burial Goods", "Foolish Return", "Forbidden Lance",
    "Instant Fusion", "Lullaby of Obedience", "Monster Reborn", "One for One",
    "Sales Ban", "Set Rotation", "Small World", "Soul Release", "Terraforming",
    "Triple Tactics Talent", "Triple Tactics Thrust", "Where Arf Thou?",
    # Other Traps
    "Transaction Rollback", "Trap Trick"
]

# Normalize to lowercase for matching
STAPLES_LOWER = {s.lower(): s for s in STAPLES}


def get_all_records(fields):
    """Fetch all card records with pagination."""
    url = f"https://api.airtable.com/v0/{BASE_ID}/{CARDS_TABLE}"
    records = []
    params = {"fields[]": fields}

    while True:
        response = requests.get(url, headers=HEADERS, params=params)
        data = response.json()

        if response.status_code != 200:
            print(f"Error: {data}")
            break

        records.extend(data.get("records", []))
        offset = data.get("offset")
        if offset:
            params["offset"] = offset
            time.sleep(0.25)
        else:
            break

    return records


def update_batch(updates):
    """Update up to 10 records at a time."""
    url = f"https://api.airtable.com/v0/{BASE_ID}/{CARDS_TABLE}"
    payload = {"records": updates}

    while True:
        response = requests.patch(url, headers=HEADERS, json=payload)
        if response.status_code == 429:
            print("  Rate limited — waiting 30 seconds...")
            time.sleep(30)
            continue
        elif response.status_code != 200:
            print(f"  Error {response.status_code}: {response.text[:200]}")
            return False
        return True


def main():
    print("📦 Loading all cards from Airtable...")
    all_cards = get_all_records(["Name", "Archetype"])
    print(f"✅ Loaded {len(all_cards)} cards.")

    # Find cards that are in the staples list AND have no archetype
    to_update = []
    matched_names = []
    not_found = []

    for card in all_cards:
        fields = card.get("fields", {})
        name = fields.get("Name", "")
        archetype = fields.get("Archetype", "")

        if name.lower() in STAPLES_LOWER and not archetype:
            to_update.append({
                "id": card["id"],
                "fields": {"Archetype": "Staples"}
            })
            matched_names.append(name)

    # Report any staples not found in the database
    matched_lower = {n.lower() for n in matched_names}
    for staple in STAPLES:
        if staple.lower() not in matched_lower:
            not_found.append(staple)

    print(f"\n🎯 Found {len(to_update)} cards to tag as Staples.")

    if not to_update:
        print("⚠️  Nothing to update — either all are already tagged or none matched.")
        return

    # Upload in batches of 10
    total_batches = (len(to_update) + 9) // 10
    updated = 0

    for i in range(0, len(to_update), 10):
        batch = to_update[i:i + 10]
        batch_num = (i // 10) + 1
        print(f"  Updating batch {batch_num}/{total_batches}...")
        if update_batch(batch):
            updated += len(batch)
        time.sleep(0.25)

    print(f"\n✅ Successfully tagged {updated} cards as Staples!")

    if matched_names:
        print("\n📋 Tagged cards:")
        for name in matched_names:
            print(f"  ✔ {name}")

    if not_found:
        print(f"\n⚠️  {len(not_found)} staples not found in your database (may have different names):")
        for name in not_found:
            print(f"  ✘ {name}")

    print("\n🚀 Now re-run deck_builder.py to build your decks!")


if __name__ == "__main__":
    main()
