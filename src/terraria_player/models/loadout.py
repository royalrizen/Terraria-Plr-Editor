from __future__ import annotations

from dataclasses import dataclass, field

from terraria_player.models.item import Item


@dataclass
class Loadout:
    """A Terraria equipment loadout."""

    armor: list[Item | None] = field(default_factory=list)
    vanity: list[Item | None] = field(default_factory=list)
    dyes: list[Item | None] = field(default_factory=list)