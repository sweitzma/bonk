import subprocess
from time import time
from collections import defaultdict
from tempfile import TemporaryDirectory
from enum import IntFlag
from inspect import cleandoc
from hashlib import sha256
from datetime import datetime

import toml
import click
import rich
from rich import print
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

from bonk import persist
from bonk import read as read_entries


def compute_id(entry):
    return sha256(entry['url'].encode()).hexdigest()


console = Console(soft_wrap=True)


class Marks(IntFlag):
    ANY = 1
    READ = 2
    FAVORITE = 4
    ARCHIVE = 8


@click.group()
def cli():
    ...

@cli.command()
@click.option('-r', '--read', is_flag=True, default=False)
@click.option('-f', '--favorite', is_flag=True, default=False)
@click.option('--id', is_flag=True, default=False)
def ls(read, favorite, id):
    """
    List out saved data.
    """

    data = read_entries()

    by_tag = defaultdict(list)

    filtered_data = []
    for entry in data:
        marks = Marks(entry['marks'])

        # by default filter out read entries
        if not read and Marks.READ in marks:
            continue

        # filter
        if read and not Marks.READ in marks:
            continue
        if favorite and not Marks.FAVORITE in marks:
            continue

        filtered_data.append(entry)

    console.print(f"Bonk showing {len(filtered_data)} of {len(data)} entries.\n")

    for entry in filtered_data:
        for tag in entry['tags']:
            by_tag[tag].append(entry)

    for tag, entries in by_tag.items():
        tag_text = f"[b i blue]{tag.upper() or 'UNTAGGED'}"

        panel_text = "\n"
        for entry in sorted(entries, key=lambda x : x['created_at']):
            at = datetime.fromtimestamp(entry['created_at'])
            at_text = at.strftime("[green dim]%b %Y[/]")
            if id:
                panel_text += f"[i red]{entry['id'][:6]}[/]  "
            panel_text += f"{at_text}  [link={entry['url']}]{entry['title']}[/link]\n"

        console.print(Panel(panel_text, title=tag_text))
        print("\n")

@cli.command()
def add():
    data = read_entries()

    entry = {}

    # Prompt
    entry['title'] = Prompt.ask("[b]Title")
    entry['url'] = Prompt.ask('[b]URL')

    entry['tags'] = ['testing']
    entry['marks'] = Marks.ANY

    entry['created_at'] = int(time())
    entry['updated_at'] = entry['created_at']
    entry['id'] = compute_id(entry)

    data.append(entry)

    # create ID
    # prompt for notes
    # promot for marks
    persist(data)


@cli.command()
@click.argument('id')
def rm(id):
    if len(id) < 6:
        print("Error, must specify an ID of at least 6 characters")
        return

    entries = read_entries()

    none_found = True
    for idx, e in enumerate(entries):
        if e['id'].startswith(id):
            console.print(f"[b]Deleted entry[/] [i red]{id}")
            console.print(entries[idx])
            del entries[idx]
            none_found = False
            break

    if none_found:
        print("[yellow]No records found to delete.")

    persist(entries)


def mark():
    """
    -f favorite
    -r read
    -u unread
    -a archive
    """
    pass

@cli.command()
@click.argument('id')
def edit(id):
    if len(id) < 6:
        print("Error, must specify an ID of at least 6 characters")
        return

    entries = read_entries()

    none_found = True
    for idx, e in enumerate(entries):
        if e['id'].startswith(id):
            with TemporaryDirectory() as dirname:
                file_name = dirname + '/entry.toml'

                with open(file_name, 'w') as f:
                    toml.dump(e, f)

                command_line=['nvim', file_name]
                p = subprocess.Popen(command_line)
                p.wait()

                with open(file_name) as f:
                    new_e = toml.load(f)

                # TODO: validate
                entries[idx] = new_e

            none_found = False
            break

    if none_found:
        print("[yellow]No records found to delete.")

    persist(entries)


