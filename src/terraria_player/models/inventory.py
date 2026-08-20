from __future__ import annotations

from dataclasses import dataclass

from terraria_player.models.item import Item


@dataclass
class Inventory:
    """A grid of item slots."""

    slots: list[list[Item | None]]