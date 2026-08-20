from __future__ import annotations

import struct
from pathlib import Path
from typing import Any

from terraria_player.crypto import (
    decrypt_player,
    encrypt_player,
)


class PlayerEditor:

    def __init__(self, parser):
        self.parser = parser

        self.data = bytearray(
            parser.decrypt()
        )

        self.offsets = self._copy_offsets(
            parser.edit_offsets
        )

        self.version = parser.version

    def _copy_offsets(
        self,
        offsets: dict[Any, Any],
    ):
        result = {}

        for key, value in offsets.items():
            if isinstance(value, dict):
                result[key] = value.copy()
            else:
                result[key] = value

        return result

    # ---------------------------------------------------------
    # binary writers :)
    # ---------------------------------------------------------

    def _write_u8(
        self,
        offset: int,
        value: int,
    ):
        if not 0 <= value <= 255:
            raise ValueError(
                "u8 value must be between 0 and 255"
            )

        struct.pack_into(
            "<B",
            self.data,
            offset,
            value,
        )

    def _write_i16(
        self,
        offset: int,
        value: int,
    ):
        struct.pack_into(
            "<h",
            self.data,
            offset,
            value,
        )

    def _write_i32(
        self,
        offset: int,
        value: int,
    ):
        struct.pack_into(
            "<i",
            self.data,
            offset,
            value,
        )

    def _write_i64(
        self,
        offset: int,
        value: int,
    ):
        struct.pack_into(
            "<q",
            self.data,
            offset,
            value,
        )

    def _write_f32(
        self,
        offset: int,
        value: float,
    ):
        struct.pack_into(
            "<f",
            self.data,
            offset,
            value,
        )

    # ---------------------------------------------------------
    # 7-bit encoded integers
    # ---------------------------------------------------------

    def _read_7bit_at(
        self,
        offset: int,
    ):
        result = 0
        shift = 0
        size = 0

        while True:
            if offset + size >= len(self.data):
                raise ValueError(
                    "Invalid 7-bit encoded integer"
                )

            byte = self.data[
                offset + size
            ]

            size += 1

            result |= (
                (byte & 0x7F)
                << shift
            )

            if not byte & 0x80:
                return result, size

            shift += 7

            if shift >= 35:
                raise ValueError(
                    "Invalid 7-bit encoded integer"
                )

    def _encode_7bit_int(
        self,
        value: int,
    ) -> bytes:
        if value < 0:
            raise ValueError(
                "7-bit encoded integer "
                "cannot be negative"
            )

        result = bytearray()

        while value >= 0x80:
            result.append(
                (value & 0x7F) | 0x80
            )

            value >>= 7

        result.append(value)

        return bytes(result)

    # ---------------------------------------------------------
    # Offset management
    # ---------------------------------------------------------

    def _shift_offset_value(
        self,
        value,
        start: int,
        end: int,
        delta: int,
    ):
        if value is None:
            return None

        if start <= value < end:
            return value

        if value >= end:
            return value + delta

        return value

    def _shift_offsets(
        self,
        start: int,
        end: int,
        delta: int,
    ):
        for key, value in list(
            self.offsets.items()
        ):
            if isinstance(value, dict):
                updated = {}

                for field, offset in value.items():
                    updated[field] = (
                        self._shift_offset_value(
                            offset,
                            start,
                            end,
                            delta,
                        )
                    )

                self.offsets[key] = updated

            elif isinstance(value, int):
                self.offsets[key] = (
                    self._shift_offset_value(
                        value,
                        start,
                        end,
                        delta,
                    )
                )

    # ---------------------------------------------------------
    # functions related to character editing
    # ---------------------------------------------------------

    def set_name(
        self,
        name: str,
    ):
        if not isinstance(name, str):
            raise TypeError(
                "Name must be a string."
            )

        offset = self.offsets["name"]

        old_length, old_prefix_size = (
            self._read_7bit_at(offset)
        )

        encoded = name.encode("utf-8")

        new_length = len(encoded)

        new_prefix = self._encode_7bit_int(
            new_length
        )

        old_start = offset

        old_end = (
            offset
            + old_prefix_size
            + old_length
        )

        replacement = (
            new_prefix + encoded
        )

        delta = (
            len(replacement)
            - (old_end - old_start)
        )

        self.data[
            old_start:old_end
        ] = replacement

        if delta != 0:
            self._shift_offsets(
                old_end,
                old_end,
                delta,
            )

        self.offsets["name"] = offset

    def set_hair_style(
        self,
        value: int,
    ):
        self._write_i32(
            self.offsets["hair_style"],
            value,
        )

    def set_hair_dye(
        self,
        value: int,
    ):
        if self.version < 83:
            raise ValueError(
                "Hair dye is not stored in this "
                "player version."
            )

        self._write_u8(
            self.offsets["hair_dye"],
            value,
        )

    def set_team(
        self,
        value: int,
    ):
        if self.version < 283:
            raise ValueError(
                "Team is not stored in this "
                "player version."
            )

        if not 0 <= value <= 5:
            raise ValueError(
                "Team must be between 0 and 5."
            )

        self._write_u8(
            self.offsets["team"],
            value,
        )

    # ---------------------------------------------------------
    # stats and stuff
    # ---------------------------------------------------------

    def set_life(
        self,
        value: int,
    ):
        if value < 0:
            raise ValueError(
                "Life cannot be negative."
            )

        self._write_i32(
            self.offsets["life"],
            value,
        )

    def set_max_life(
        self,
        value: int,
    ):
        if value < 0:
            raise ValueError(
                "Max life cannot be negative."
            )

        self._write_i32(
            self.offsets["max_life"],
            value,
        )

    def set_mana(
        self,
        value: int,
    ):
        if value < 0:
            raise ValueError(
                "Mana cannot be negative."
            )

        self._write_i32(
            self.offsets["mana"],
            value,
        )

    def set_max_mana(
        self,
        value: int,
    ):
        if value < 0:
            raise ValueError(
                "Max mana cannot be negative."
            )

        self._write_i32(
            self.offsets["max_mana"],
            value,
        )

    # ---------------------------------------------------------
    # inventory
    # ---------------------------------------------------------

    def set_inventory_item(
        self,
        row: int,
        slot: int,
        item_id: int | None = None,
        count: int | None = None,
        prefix: int | None = None,
        favorite: bool | None = None,
    ):
        key = (
            "inventory",
            row,
            slot,
        )

        if key not in self.offsets:
            raise IndexError(
                f"Inventory slot "
                f"[{row}:{slot}] does not exist."
            )

        info = self.offsets[key]

        if item_id is not None:
            if self.version < 38:
                raise NotImplementedError(
                    "Changing item IDs in Terraria "
                    "versions below 38 requires "
                    "rewriting the item string."
                )

            self._write_i32(
                info["item_id"],
                item_id,
            )

        if count is not None:
            if count < 0:
                raise ValueError(
                    "Item count cannot be negative."
                )

            self._write_i32(
                info["count"],
                count,
            )

        if prefix is not None:
            if info["prefix"] is None:
                raise ValueError(
                    "This Terraria version "
                    "does not contain prefixes."
                )

            self._write_u8(
                info["prefix"],
                prefix,
            )

        if favorite is not None:
            if info["favorite"] is None:
                raise ValueError(
                    "This Terraria version "
                    "does not contain favorite flags."
                )

            self._write_u8(
                info["favorite"],
                1 if favorite else 0,
            )

    # ---------------------------------------------------------
    # coins :p
    # ---------------------------------------------------------

    def set_coin(
        self,
        slot: int,
        item_id: int | None = None,
        count: int | None = None,
    ):
        if not 0 <= slot < 4:
            raise IndexError(
                "Coin slot must be 0-3."
            )

        raise NotImplementedError(
            "Coin offset editing is not enabled "
            "in this version of the editor."
        )

    # ---------------------------------------------------------
    # save that damn file
    # ---------------------------------------------------------

    def save(
        self,
        output_file: str | Path,
    ):
        output_file = Path(
            output_file
        )

        encrypted = encrypt_player(
            bytes(self.data)
        )

        output_file.write_bytes(
            encrypted
        )