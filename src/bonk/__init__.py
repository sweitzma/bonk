import json
import os
from pathlib import Path

from bonk.entry import Entry


BONK_DIR = Path.home() / ".bonk"
BONK_DB_FILE = BONK_DIR / "storage.json"
BONK_NOTE_DIR = BONK_DIR / "notes"


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


# ensure bonk local storage exists
if not BONK_DIR.exists():
    os.mkdir(BONK_DIR)

if not BONK_NOTE_DIR.exists():
    os.mkdir(BONK_NOTE_DIR)

if not BONK_DB_FILE.exists():
    persist([])
