from typing import TypedDict

__all__ = ("Section", "Patch",)

class Section(TypedDict):
    search: str
    replace: str
    max: int

Patch = list[Section]
