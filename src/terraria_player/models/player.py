from __future__ import annotations

from dataclasses import dataclass, field

from terraria_player.models.item import Item
from terraria_player.models.loadout import Loadout


@dataclass
class Player:
    """Parsed Terraria player data."""

    version: int

    name: str = ""
    difficulty: str = ""

    life: int = 0
    max_life: int = 0
    mana: int = 0
    max_mana: int = 0

    hair_style: int = 0
    hair_dye: int | None = None
    team: int | None = None
    style: str = ""

    inventory: list[list[Item | None]] = field(
        default_factory=list
    )

    coins: list[Item | None] = field(
        default_factory=list
    )

    ammo: list[Item | None] = field(
        default_factory=list
    )

    loadouts: list[Loadout] = field(
        default_factory=list
    )