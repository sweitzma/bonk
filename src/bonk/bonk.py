import subprocess
from collections import defaultdict
from tempfile import TemporaryDirectory
from random import sample

import toml
import click
from rich.columns import Columns
from rich import print
from rich.console import Console
from rich.panel import Panel

from bonk import persist_json, persist_entries
from bonk import read_json, read_entries
from bonk.entry import Entry, user_defined_entry, NON_HUMAN_EDITABLE_FIELDS


console = Console(soft_wrap=True)


def safe_sample(l, n):
    n = min(len(l), n)
    return sample(l, n)


def filter_entries(entries: list[Entry], favorite: bool = False, read: bool = False):
    filtered_entries = []
    for e in entries:
        if read != e.is_read:
            continue
        elif favorite and not e.is_favorite:
            continue

        filtered_entries.append(e)

    return filtered_entries


def find_by_id(entries: list[Entry], id_prefix: str):
    if len(id_prefix) < 6:
        raise ValueError("ID prefix must be at least 6 characters.")

    matching_indices = []
    for idx, e in enumerate(entries):
        if e.id.startswith(id_prefix):
            matching_indices.append(idx)

    if len(matching_indices) == 0:
        return None, None
    elif len(matching_indices) == 1:
        return matching_indices[0], entries[matching_indices[0]]
    else:
        raise ValueError("ID prefix corresponds with multiple entries.")


@click.group()
def cli():
    ...


@cli.command()
@click.option("-r", "--read", is_flag=True, default=False)
@click.option("-f", "--favorite", is_flag=True, default=False)
@click.option("--id", is_flag=True, default=False)
def ls(read, favorite, id):
    """
    List all entries, ordered by tags.
    """
    entries = read_entries()
    all_entries_size = len(entries)
    entries = filter_entries(entries, read=read, favorite=favorite)
    filtered_entries_size = len(entries)
    console.print(
        f"bonk showing {filtered_entries_size} of {all_entries_size} entries.\n"
    )

    by_tag = defaultdict(list)
    for entry in entries:
        if len(entry.tags) == 0:
            by_tag["untagged"].append(entry)
        else:
            for tag in entry.tags:
                by_tag[tag.lower()].append(entry)

    tag_order = sorted(by_tag.keys())
    for tag in tag_order:
        entries_w_tag = sorted(by_tag[tag], key=lambda e: e.created_at)
        tag_text = f"[b i blue]{tag.upper()}"

        panel_text = "\n"
        for e in entries_w_tag:
            panel_text += e.short_view(id) + "\n"

        console.print(Panel(panel_text, title=tag_text))
        print("\n")


@cli.command()
@click.option("-r", "--read", is_flag=True, default=False)
@click.option("-f", "--favorite", is_flag=True, default=False)
@click.option("-n", "--num", default=3)
def rand(read, favorite, num):
    """
    Return random sample of entries.
    """
    entries = read_entries()
    entries = filter_entries(entries, read=read, favorite=favorite)
    entries = safe_sample(entries, num)

    console.print()
    for entry in entries:
        console.print(entry.long_view())
        console.print()


@cli.command()
def add():
    data = read_json()
    entry = user_defined_entry()
    console.print(entry.long_view())
    data.append(entry.to_dict())
    persist_json(data)


@cli.command()
@click.argument("id")
def rm(id):
    entries = read_entries()
    try:
        idx, entry = find_by_id(entries, id)
    except ValueError as e:
        print("[b red]ERROR:[/]", e)
        return

    if idx is None or entry is None:
        print("[yellow]No records found to delete.")
        return

    console.print(f"[b]deleted entry[/] {entry.id_view}")
    console.print(entries[idx].to_dict())
    del entries[idx]

    persist_entries(entries)


@cli.command()
@click.argument("id")
def edit(id):
    entries = read_entries()
    try:
        idx, entry = find_by_id(entries, id)
    except ValueError as e:
        print("[b red]ERROR:[/]", e)
        return

    if idx is None or entry is None:
        print("[yellow]No records found to delete.")
        return

    # remove some fields from editing
    editable_dict = entry.to_dict()
    add_back_in_dict = {}
    for field in NON_HUMAN_EDITABLE_FIELDS:
        add_back_in_dict[field] = editable_dict[field]
        del editable_dict[field]

    with TemporaryDirectory() as dirname:
        file_name = dirname + "/entry.toml"
        with open(file_name, "w") as f:
            toml.dump(editable_dict, f)

        # open editor
        command_line = ["nvim", file_name]
        p = subprocess.Popen(command_line)
        p.wait()

        # read results back in
        with open(file_name) as f:
            edited_dict = toml.load(f)

        # fill in non-editable fields
        for k, v in add_back_in_dict.items():
            edited_dict[k] = v

        # create Entry object and bump timestamp
        updated_entry = Entry(**edited_dict)
        updated_entry.set_updated_at()
        updated_entry.validate()
        entries[idx] = updated_entry

    persist_entries(entries)


@cli.command()
@click.argument("id")
@click.option("-r", "--raw", is_flag=True, default=False)
def view(id, raw):
    entries = read_entries()
    try:
        idx, entry = find_by_id(entries, id)
    except ValueError as e:
        print("[b red]ERROR:[/]", e)
        return

    if idx is None or entry is None:
        print("[yellow]No records found to delete.")
        return

    if raw:
        console.print(entry.to_dict())
    else:
        console.print(entry.long_view())


@cli.command()
def tags():
    entries = read_entries()
    by_tag, untagged = defaultdict(int), 0
    for entry in entries:
        if len(entry.tags) == 0:
            untagged += 1

        for tag in entry.tags:
            by_tag[tag.lower()] += 1
    tag_order = sorted(by_tag.keys())
    tags = [f"[i b blue]{tag}[/] [dim]({by_tag[tag]})[/]" for tag in tag_order]

    console.print(f"[b i dim blue]Untagged[/] [dim]({untagged})[/]\n", justify="center")
    columns = Columns(tags, equal=True, expand=True)
    console.print(columns)


def mark():
    """
    Not Implemented.

    Mark entries with read, favorite, archive, ...
    """
    ...


def notes():
    """
    Not Implemented.

    Create a note for a particular entry.
    """
    ...
