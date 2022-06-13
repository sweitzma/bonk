from dataclasses import dataclass
from typing import Union
from datetime import datetime

from rich.panel import Panel


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
        tags = [f"[blue]{t}[/]" for t in self.tags]
        tag_text = ", ".join(tags)
        return tag_text

    def validate(self):
        ...

    def short_view(self, show_id=False):
        if show_id:
            return f"{self.id_view}  {self.created_at_view}  {self.link_view}"
        else:
            return f"{self.created_at_view}  {self.link_view}"

    def long_view(self):
        text = str()
        text += "\n"
        text += f"[b dim]Title:[/] {self.link_view}\n"
        text += f"[b dim]Added:[/] {self.created_at_long_view}\n"
        text += f"[b dim]Marks:[/] {self.marks}\n"
        text += f"[b dim]Tags:[/] {self.tag_view}"
        text += "\n"
        return Panel(text, title=self.id_view)
