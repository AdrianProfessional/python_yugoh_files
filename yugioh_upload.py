import json
import time
import requests

# Configuration
API_KEY = "patniv0RRRddkos0B.5d09712d4ccf964c464c59eaef1efce09d7b6884192b067d7ea64259f335dbb3"
BASE_ID = "appY9amPlFG4Fnt6W"
TABLE_ID = "tblvI7sjF5W1OiO2u"
INPUT_FILE = "YuGIDatabase.txt"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"


def parse_card(card):
    """Extract only the fields we need from a card."""
    banlist = card.get("banlist_info", {})
    ban_status = (
        banlist.get("ban_tcg") or
        banlist.get("ban_ocg") or
        ""
    )

    image_url = ""
    images = card.get("card_images", [])
    if images:
        image_url = images[0].get("image_url", "")

    return {
        "Card ID": card.get("id"),
        "Name": card.get("name", ""),
        "Type": card.get("type", ""),
        "Human Readable Card Type": card.get("humanReadableCardType", ""),
        "Frame Type": card.get("frameType", ""),
        "Description": card.get("desc", ""),
        "ATK": card.get("atk"),
        "DEF": card.get("def"),
        "Level": card.get("level"),
        "Attribute": card.get("attribute", ""),
        "Race": card.get("race", ""),
        "Archetype": card.get("archetype", ""),
        "Image URL": image_url,
        "Ban Status": ban_status,
    }


def clean_record(fields):
    """Remove None values — Airtable rejects null for number fields."""
    return {k: v for k, v in fields.items() if v is not None and v != ""}


def upload_batch(records):
    """Upload a batch of up to 10 records to Airtable."""
    payload = {
        "records": [{"fields": clean_record(r)} for r in records]
    }
    while True:
        response = requests.post(BASE_URL, headers=HEADERS, json=payload)
        if response.status_code == 429:
            print("  Rate limited — waiting 30 seconds...")
            time.sleep(30)
            continue
        elif response.status_code != 200:
            print(f"  Error {response.status_code}: {response.text[:200]}")
            return False
        return True


def main():
    print(f"Loading {INPUT_FILE}...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)

    cards = raw.get("data", [])
    print(f"Found {len(cards)} cards.")

    # Parse all cards
    records = [parse_card(c) for c in cards]

    # Upload in batches of 10
    batch_size = 10
    total_batches = (len(records) + batch_size - 1) // batch_size
    success_count = 0

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        batch_num = (i // batch_size) + 1

        print(f"  Uploading batch {batch_num}/{total_batches} ({i+1}–{min(i+batch_size, len(records))})...")

        if upload_batch(batch):
            success_count += len(batch)
        else:
            print(f"  Batch {batch_num} failed — continuing...")

        # Polite delay to stay within rate limits (5 req/sec)
        time.sleep(0.25)

    print(f"\nDone! {success_count}/{len(records)} cards uploaded.")


if __name__ == "__main__":
    main()
