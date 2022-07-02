import requests
import os

from dotenv import dotenv_values
from rich import print
from rich.prompt import Prompt, Confirm

from bonk.marks import Marks
from bonk.entry import Entry, compute_id
from bonk import last_pocket_fetch, BONK_DOTENV



POCKET_API_URL = "https://getpocket.com/v3/get"


def process_raw_entry(entry):
    return {
        'title': entry['resolved_title'],
        'url': entry['resolved_url'],
        'created_at': int(entry['time_added']),
        'updated_at': int(entry['time_updated']),
    }


def new_pocket_entries():
    creds = dotenv_values(BONK_DOTENV)
    params = {
        'consumer_key': creds['POCKET_CONSUMER_KEY'],
        'access_token': creds['POCKET_ACCESS_TOKEN'],
        'since': last_pocket_fetch(),
        'detailType': 'simple',
    }
    response = requests.request("POST", POCKET_API_URL, params=params)
    response_obj = response.json()

    if len(response_obj['list']) == 0:
        return []

    entries = [process_raw_entry(e) for e in response_obj['list'].values()]
    return entries


def fetch_and_confirm_new_pocket_entries():
    new_entry_data = new_pocket_entries()

    entries = []
    for data in new_entry_data:
        print(f"\nIncoming entry: [link={data['url']}]{data['title']}[/link]")
        if not Confirm.ask("Do you want to save this entry?"):
            continue

        data["tags"] = []
        while True:
            new_tag = Prompt.ask("[b]Add tag[/] (or press <Enter> to stop)")
            if len(new_tag.strip()) == 0:
                break
            data["tags"].append(new_tag)

        marks = Marks.ANY
        if Confirm.ask("Mark as read?"):
            marks |= Marks.READ
        if Confirm.ask("Mark as favorite?"):
            marks |= Marks.FAVORITE
        data["marks"] = int(marks)

        data["id"] = compute_id(data)

        entry = Entry(**data)
        entry.set_updated_at()
        entry.validate()
        entries.append(entry)

    return entries
