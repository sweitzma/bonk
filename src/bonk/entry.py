from dataclasses import dataclass, asdict
from typing import Union
from datetime import datetime
from time import time
from hashlib import sha256

from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from bonk.marks import Marks


NON_HUMAN_EDITABLE_FIELDS = ["id", "created_at", "updated_at", "note_file"]


@dataclass
class Entry:
    title: str
    url: str
    tags: list
    marks: int
    created_at: int
    updated_at: int
    id: str
    description: object = None
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

    @property
    def is_read(self):
        return self.is_marked_with(Marks.READ)

    @property
    def is_favorite(self):
        return self.is_marked_with(Marks.FAVORITE)

    def validate(self):
        ...

    def is_marked_with(self, mark: Marks):
        return mark in Marks(self.marks)

    def mark_with(self, mark_type: str):
        m = Marks(self.marks)
        if mark_type == "read":
            m |= Marks.READ
        if mark_type == "unread":
            m &= ~Marks.READ
        if mark_type == "favorite":
            m |= Marks.FAVORITE
        if mark_type == "archive":
            m |= Marks.ARCHIVE
        self.marks = int(m)
        self.set_updated_at()

    def short_view(self, show_id=False):
        if show_id:
            return f"{self.id_view}  {self.created_at_view}  {self.link_view}"
        else:
            return f"{self.created_at_view}  {self.link_view}"

    @property
    def marks_view(self):
        marks = Marks(self.marks)
        mark_texts = []

        if Marks.READ in marks:
            mark_texts.append("📖 Read")
        else:
            mark_texts.append("📘 Unread")

        if Marks.FAVORITE in marks:
            mark_texts.append("⭐ Favorite")

        if Marks.ARCHIVE in marks:
            mark_texts.append("🗄️ Archive")

        return ", ".join(mark_texts)

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

    def to_dict(self):
        return asdict(self)

    def set_updated_at(self):
        self.updated_at = int(time())


def compute_id(entry):
    return sha256(entry["url"].encode()).hexdigest()[:32]


def user_defined_entry():
    data = {}

    data["title"] = Prompt.ask("[b]Title")
    data["url"] = Prompt.ask("[b]URL")

    add_tags = True
    data["tags"] = []
    while add_tags:
        new_tag = Prompt.ask("[b]Add tag")
        data["tags"].append(new_tag)
        add_tags = Confirm.ask("Do you want to add another?")

    marks = Marks.ANY
    if Confirm.ask("Mark as read?"):
        marks |= Marks.READ
    if Confirm.ask("Mark as favorite?"):
        marks |= Marks.FAVORITE
    data["marks"] = int(marks)

    data["created_at"] = int(time())
    data["updated_at"] = data["created_at"]
    data["id"] = compute_id(data)

    entry = Entry(**data)
    entry.validate()
    return entry
