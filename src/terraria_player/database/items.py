from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ItemDatabase:

    def __init__(
        self,
        path: str | Path,
    ):
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"Item database not found: {path}"
            )

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        self.version = data.get(
            "_terrariaversion"
        )

        self.generated = data.get(
            "_generated"
        )

        self.items: dict[
            int,
            dict[str, Any],
        ] = {}

        self.names: dict[
            str,
            int,
        ] = {}

        for key, item in data.items():

            if not key.isdigit():
                continue

            item_id = int(key)

            self.items[item_id] = item

            internal_name = item.get(
                "internalName"
            )

            if internal_name:
                self.names[
                    internal_name
                ] = item_id

    def get(
        self,
        item_id: int,
    ) -> dict[str, Any] | None:
        return self.items.get(item_id)

    def get_by_name(
        self,
        name: str,
    ) -> dict[str, Any] | None:
        item_id = self.names.get(name)

        if item_id is None:
            return None

        return self.get(item_id)

    def get_name(
        self,
        item_id: int,
    ) -> str:
        item = self.get(item_id)

        if item is None:
            return (
                f"Unknown Item ({item_id})"
            )

        return item.get(
            "name",
            f"Unknown Item ({item_id})",
        )

    def get_internal_name(
        self,
        item_id: int,
    ) -> str:
        item = self.get(item_id)

        if item is None:
            return ""

        return item.get(
            "internalName",
            "",
        )