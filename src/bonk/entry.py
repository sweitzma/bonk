from dataclasses import dataclass, asdict
from typing import Union
from datetime import datetime
from time import time
from hashlib import sha256

from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from bonk.marks import Marks


@dataclass
class Entry:
    title: str
    url: str
    tags: list
    marks: int
    created_at: int
    updated_at: int
    id: str
    metadata: object = None
    note_file: Union[str, None] = None

    @property
    def id_view(self):
        return f"[i red]{self.id[:6]}[/]"

    @property
    def link_view(self):
        return f"[link={self.url}]{self.title}[/link]"

    @property
    def created_at_view(self):
        fmt = "%b %Y"
        at = datetime.fromtimestamp(self.created_at)
        return at.strftime(f"[i green]{fmt}[/]") 

    @property
    def created_at_long_view(self):
        fmt = "%B %d, %Y"
        at = datetime.fromtimestamp(self.created_at)
        return at.strftime(f"[i green]{fmt}[/]") 

    @property
    def tag_view(self):
        tags = [f"[i blue]#{t}[/]" for t in self.tags]
        tag_text = ", ".join(tags)
        return tag_text

    def validate(self):
        ...

    def short_view(self, show_id=False):
        if show_id:
            return f"{self.id_view}  {self.created_at_view}  {self.link_view}"
        else:
            return f"{self.created_at_view}  {self.link_view}"

    @property
    def marks_view(self):
        marks = Marks(self.marks)
        text = str()

        if Marks.READ in marks:
            text += "📖"
        else:
            text += "📘"

        if Marks.FAVORITE in marks:
            text += "⭐"

        if Marks.ARCHIVE in marks:
            text += "🗄️"

        return text

    def long_view(self):
        title = f"[dim]{self.id_view}[/]"

        text = str()
        text += "\n"
        text += f"[b dim]Title:[/] {self.link_view}\n"
        text += f"[b dim]Added:[/] {self.created_at_long_view}\n"
        text += f"[b dim]Marks:[/] {self.marks_view}\n"
        text += f"[b dim]Tags:[/] {self.tag_view}"
        text += "\n"
        return Panel(text, title=title)


def compute_id(entry):
    return sha256(entry['url'].encode()).hexdigest()[:32]


def user_defined_entry():
    data={}

    data['title'] = Prompt.ask("[b]Title")
    data['url'] = Prompt.ask('[b]URL')
    
    add_tags = True
    data['tags'] = []
    while add_tags:
        new_tag = Prompt.ask('[b]Add tag')
        data['tags'].append(new_tag)
        add_tags = Confirm.ask("Do you want to add another?")

    marks = Marks.ANY
    if Confirm.ask("Mark as read?"):
        marks |= Marks.READ
    if Confirm.ask("Mark as favorite?"):
        marks |= Marks.FAVORITE
    data['marks'] = int(marks)

    data['created_at'] = int(time())
    data['updated_at'] = data['created_at']
    data['id'] = compute_id(data)

    entry = Entry(**data)
    entry.validate()
    entry_obj = asdict(entry)

    # TODO: show long view

    return entry_obj

