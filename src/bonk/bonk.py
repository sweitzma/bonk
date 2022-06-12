import subprocess
from tempfile import TemporaryDirectory

import click
from rich.prompt import Prompt

from bonk import read, persist


@click.group()
def cli():
    ...

@cli.command()
def ls():
    """
    List out saved data.


    [TAG]
    """
    data = read()
    print(f"Bonk contains {len(data)} entries:")
    for entry in data:
        print(f" * {entry}")

@cli.command()
def add():
    data = read()

    entry = {}
    entry['title'] = Prompt.ask("[bold]Title")
    entry['tags'] = Prompt.ask("[bold]Tags")
    entry['url'] = Prompt.ask('[bold]URL')

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


