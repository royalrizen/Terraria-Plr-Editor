from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ParsedItem:
    id: int
    name: str
    internal_name: str
    count: int
    prefix: int | None = None
    favorite: bool = False