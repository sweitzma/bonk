import subprocess
from time import time
from collections import defaultdict
from tempfile import TemporaryDirectory
from enum import IntFlag

import click
from rich import print
from rich.console import Console
from rich.prompt import Prompt

from bonk import persist
from bonk import read as read_entries


console = Console()


class Marks(IntFlag):
    READ = 1
    FAVORITE = 2
    ARCHIVE = 4


@click.group()
def cli():
    ...

@cli.command()
@click.option('-r', '--read', is_flag=True, default=False)
def ls(read):
    """
    List out saved data.
    """
    data = read_entries()
    print(f"Bonk contains {len(data)} entries:")

    by_tag = defaultdict(list)

    for entry in data:
        if read and Marks.READ not in Marks(entry['marks']):
            continue

        for tag in entry['tags']:
            by_tag[tag].append(entry)

    for tag, entries in by_tag.items():
        console.print(f"[bold]{tag.upper() or 'UNTAGGED'}", justify='center')
        for entry in entries:
            console.print(f"- [link={entry['url']}]{entry['title']}[/link]")
        print()

@cli.command()
def add():
    data = read()

    entry = {}
    entry['title'] = Prompt.ask("[bold]Title")
    entry['tags'] = ['testing']
    entry['url'] = Prompt.ask('[bold]URL')
    entry['marks'] = 0
    entry['created_at'] = int(time())
    entry['updated_at'] = entry['created_at']

    data.append(entry)

    # create ID
    # prompt for notes
    # promot for marks
    persist(data)

def mark():
    """
    -f favorite
    -r read
    -u unread
    -a archive
    """
    pass

def note():
    with TemporaryDirectory() as dirname:
        file_name = dirname + '/tmp.py'
        command_line=['nvim', file_name]
        p = subprocess.Popen(command_line)
        p.wait()


