import subprocess
from collections import defaultdict
from tempfile import TemporaryDirectory
from random import sample

import toml
import click
from rich import print
from rich.console import Console
from rich.panel import Panel

from bonk import persist
from bonk import read as read_entries
from bonk.entry import Entry, user_defined_entry
from bonk.marks import Marks


console = Console(soft_wrap=True)


def safe_sample(l, n):
    n = min(len(l), n)
    return sample(l, n)


@click.group()
def cli():
    ...


@cli.command()
@click.option('-r', '--read', is_flag=True, default=False)
@click.option('-f', '--favorite', is_flag=True, default=False)
@click.option('--id', is_flag=True, default=False)
def ls(read, favorite, id):
    """
    list out saved data.
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

    console.print(f"bonk showing {len(filtered_data)} of {len(data)} entries.\n")

    for entry in filtered_data:
        for tag in entry['tags']:
            by_tag[tag].append(entry)

    for tag, entries in by_tag.items():
        tag_text = f"[b i blue]{tag.upper() or 'untagged'}"

        panel_text = "\n"
        for entry in sorted(entries, key=lambda x : x['created_at']):
            panel_text += Entry(**entry).short_view(id) + "\n"

        console.print(Panel(panel_text, title=tag_text))
        print("\n")


@cli.command()
@click.option('-r', '--read', is_flag=True, default=False)
@click.option('-f', '--favorite', is_flag=True, default=False)
@click.option('--id', is_flag=True, default=False)
@click.option('-n', '--num', default=3)
def rand(read, favorite, id, num):
    """
    Return random sample of entries.
    """

    data = read_entries()
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

    filtered_data = safe_sample(filtered_data, num)

    console.print()
    for entry in filtered_data:
        console.print(Entry(**entry).long_view())
        console.print()


@cli.command()
def add():
    data = read_entries()
    entry = user_defined_entry()
    data.append(entry)
    persist(data)


@cli.command()
@click.argument('id')
def rm(id):
    if len(id) < 6:
        print("error, must specify an id of at least 6 characters")
        return

    entries = read_entries()

    none_found = True
    for idx, e in enumerate(entries):
        if e['id'].startswith(id):
            console.print(f"[b]deleted entry[/] [i red]{id}")
            console.print(entries[idx])
            del entries[idx]
            none_found = False
            break

    if none_found:
        print("[yellow]no records found to delete.")

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
        print("error, must specify an id of at least 6 characters")
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

                # todo: validate
                entries[idx] = new_e

            none_found = False
            break

    if none_found:
        print("[yellow]no records found to delete.")

    persist(entries)

# functions
#  - find by ID
#  - filter by marks

# api additions
#  - bonk tags
#  - bonk ls -t <tag>
