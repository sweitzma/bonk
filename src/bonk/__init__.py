import json
import os
import time
from pathlib import Path

from bonk.entry import Entry


BONK_DIR = Path.home() / ".bonk"
BONK_DB_FILE = BONK_DIR / "storage.json"
BONK_POCKET_DATA = BONK_DIR / "pocket.json"
BONK_NOTE_DIR = BONK_DIR / "notes"
BONK_DOTENV = BONK_DIR / ".env"


def persist_dangerous(obj):
    with open(BONK_DB_FILE, "w") as f:
        json.dump(obj, f, indent=2)


def persist_json(obj):
    prev_state = read_json()
    try:
        persist_dangerous(obj)
    except Exception as e:
        print("ERROR: reverting back to original state.")
        persist_dangerous(prev_state)
        raise e


def persist_entries(entries):
    persist_json([e.to_dict() for e in entries])


def read_json():
    with open(BONK_DB_FILE) as f:
        data = json.load(f)

    return data


def read_entries():
    data = read_json()
    return [Entry(**e) for e in data]


def last_pocket_fetch():
    with open(BONK_POCKET_DATA) as f:
        return json.load(f)['last_retrieval']


def bump_pocket_fetch_ts():
    with open(BONK_POCKET_DATA, 'r') as f:
        data = json.load(f)

    data['last_retrieval'] = int(time.time())

    with open(BONK_POCKET_DATA, 'w') as f:
        json.dump(data, f, indent=2)


# ensure bonk local storage exists
if not BONK_DIR.exists():
    os.mkdir(BONK_DIR)

if not BONK_NOTE_DIR.exists():
    os.mkdir(BONK_NOTE_DIR)

if not BONK_DB_FILE.exists():
    persist_dangerous([])

if not BONK_POCKET_DATA.exists():
    with open(BONK_POCKET_DATA, 'w') as f:
        json.dump({"last_retrieval": 0}, f)

