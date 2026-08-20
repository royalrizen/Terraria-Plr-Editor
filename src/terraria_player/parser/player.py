from __future__ import annotations

from pathlib import Path
from typing import Any

from terraria_player.binary import BinaryReader
from terraria_player.constants import (
    MAGIC_NUMBER,
    SUPPORTED_VERSIONS,
)

from terraria_player.crypto import (
    decrypt_player
)

from terraria_player.database import ItemDatabase
from terraria_player.models import ParsedItem


class PlayerParser:

    def __init__(
        self,
        player_file: str | Path,
        items_file: str | Path,
    ):
        self.player_file = Path(player_file)

        self.items = ItemDatabase(
            items_file
        )

        self.version = 0

        self.edit_offsets: dict[Any, Any] = {}

    def decrypt(self) -> bytes:
        return decrypt_player(
            self.player_file.read_bytes()
        )

    def get_item(
        self,
        item_id: int,
    ):
        return self.items.get(item_id)

    def read_item(
        self,
        reader: BinaryReader,
    ):
        if self.version < 38:
            internal_name = reader.cs_string()

            return self.items.get_by_name(
                internal_name
            )

        item_id = reader.i32()

        if item_id <= 0:
            return None

        return self.items.get(item_id)

    def read_prefix(
        self,
        reader: BinaryReader,
    ):
        if self.version < 36:
            return None

        return reader.u8()

    def item_id(
        self,
        item,
    ):
        if item is None:
            return -1

        for item_id, data in self.items.items.items():
            if data is item:
                return item_id

        return -1

    def make_item(
        self,
        item,
        count=1,
        prefix=None,
        favorite=False,
    ):
        if item is None:
            return None

        return ParsedItem(
            id=self.item_id(item),
            name=item.get("name", ""),
            internal_name=item.get(
                "internalName",
                "",
            ),
            count=count,
            prefix=prefix,
            favorite=favorite,
        )

    def read_item_slot(
        self,
        reader: BinaryReader,
    ):
        item = self.read_item(reader)

        count = reader.i32()

        prefix = self.read_prefix(reader)

        if item is None:
            return None

        if count <= 0:
            return None

        return self.make_item(
            item,
            count=count,
            prefix=prefix,
        )

    def read_inventory_slot(
        self,
        reader: BinaryReader,
        favorite_enabled,
    ):
        item = self.read_item_slot(reader)

        favorite = False

        if favorite_enabled:
            favorite = reader.boolean()

        if item is None:
            return None

        item.favorite = favorite

        return item

    def read_single_item_slot(
        self,
        reader: BinaryReader,
    ):
        item = self.read_item(reader)

        prefix = self.read_prefix(reader)

        if item is None:
            return None

        return self.make_item(
            item,
            count=1,
            prefix=prefix,
        )

    def read_color(
        self,
        reader: BinaryReader,
    ):
        return [
            reader.u8(),
            reader.u8(),
            reader.u8(),
        ]

    def read_difficulty(
        self,
        reader: BinaryReader,
    ):
        if self.version <= 10:
            return "SoftCore"

        if self.version <= 17:
            return (
                "Hardcore"
                if reader.boolean()
                else "SoftCore"
            )

        return {
            0: "SoftCore",
            1: "MediumCore",
            2: "Hardcore",
            3: "Journey",
        }.get(
            reader.u8(),
            "SoftCore",
        )

    def read_inventory(
        self,
        reader: BinaryReader,
    ):
        rows = (
            4
            if self.version < 58
            else 5
        )

        result = []

        for row_index in range(rows):
            row = []

            for slot_index in range(10):
                item_id_offset = reader.tell()

                item = self.read_item(reader)

                count_offset = reader.tell()

                count = reader.i32()

                prefix_offset = None
                prefix = None

                if self.version >= 36:
                    prefix_offset = reader.tell()

                    prefix = reader.u8()

                favorite_offset = None
                favorite = False

                if self.version >= 114:
                    favorite_offset = reader.tell()

                    favorite = reader.boolean()

                self.edit_offsets[
                    (
                        "inventory",
                        row_index,
                        slot_index,
                    )
                ] = {
                    "item_id": item_id_offset,
                    "count": count_offset,
                    "prefix": prefix_offset,
                    "favorite": favorite_offset,
                }

                if item is None or count <= 0:
                    row.append(None)
                else:
                    row.append(
                        self.make_item(
                            item,
                            count=count,
                            prefix=prefix,
                            favorite=favorite,
                        )
                    )

            result.append(row)

        return result

    def read_small_inventory(
        self,
        reader: BinaryReader,
    ):
        return [
            self.read_inventory_slot(
                reader,
                self.version >= 114,
            )
            for _ in range(4)
        ]

    def read_container(
        self,
        reader: BinaryReader,
    ):
        columns = (
            10
            if self.version >= 58
            else 5
        )

        result = []

        for _ in range(4):
            row = []

            for _ in range(columns):
                row.append(
                    self.read_item_slot(reader)
                )

            while len(row) < 10:
                row.append(None)

            result.append(row)

        return result

    def read_void_vault(
        self,
        reader: BinaryReader,
    ):
        inventory = [
            [None for _ in range(10)]
            for _ in range(4)
        ]

        if self.version >= 198:
            for row in range(4):
                for col in range(10):
                    inventory[row][col] = (
                        self.read_inventory_slot(
                            reader,
                            self.version >= 255,
                        )
                    )

        unlocked = False

        if self.version >= 199:
            unlocked = reader.boolean()

        if not unlocked:
            unlocked = any(
                item is not None
                for row in inventory
                for item in row
            )

        if not unlocked:
            return None

        return inventory

    def read_buffs(
        self,
        reader: BinaryReader,
    ):
        if self.version < 11:
            return []

        if self.version <= 73:
            count = 10
        elif self.version <= 251:
            count = 22
        else:
            count = 44

        buffs = []

        for _ in range(count):
            buff_id = reader.i32()

            buff_time_ticks = reader.i32()

            buffs.append({
                "id": buff_id,
                "time_ticks": buff_time_ticks,
                "time_seconds": (
                    buff_time_ticks / 60.0
                ),
            })

        return buffs

    def read_spawn_points(
        self,
        reader: BinaryReader,
    ):
        result = []

        for _ in range(200):
            x = reader.i32()

            if x == -1:
                break

            y = reader.i32()

            world_id = reader.i32()

            world_name = reader.cs_string()

            result.append({
                "x": x,
                "y": y,
                "world_id": world_id,
                "world_name": world_name,
            })

        return result

    def read_visibility(
        self,
        reader: BinaryReader,
    ):
        value = reader.i32()

        return {
            0: "Bright",
            1: "Faded",
            2: "Classic",
        }.get(
            value,
            "Bright",
        )

    def read_loadout(
        self,
        reader: BinaryReader,
    ):
        loadout = {
            "armor": [],
            "vanity": [],
            "dyes": [],
            "accessory_visibility": [],
        }

        for _ in range(3):
            loadout["armor"].append(
                self.read_item_slot(reader)
            )

        for _ in range(7):
            loadout["armor"].append(
                self.read_item_slot(reader)
            )

        for _ in range(3):
            loadout["vanity"].append(
                self.read_item_slot(reader)
            )

        for _ in range(7):
            loadout["vanity"].append(
                self.read_item_slot(reader)
            )

        for _ in range(3):
            loadout["dyes"].append(
                self.read_item_slot(reader)
            )

        for _ in range(7):
            loadout["dyes"].append(
                self.read_item_slot(reader)
            )

        for _ in range(3):
            reader.boolean()

        for _ in range(7):
            loadout[
                "accessory_visibility"
            ].append(
                not reader.boolean()
            )

        return loadout

    def read_loadouts(
        self,
        reader: BinaryReader,
        current_loadout,
    ):
        selected = reader.i32()

        loadouts = []

        for _ in range(3):
            loadouts.append(
                self.read_loadout(reader)
            )

        return {
            "selected_loadout": selected,
            "loadouts": loadouts,
            "current_loadout": current_loadout,
        }

    def read_player_header(
        self,
        reader: BinaryReader,
    ):
        magic = reader.read(7)

        if magic != MAGIC_NUMBER:
            raise ValueError(
                f"Invalid Terraria magic number: "
                f"{magic!r}"
            )

        file_type = reader.u8()

        if file_type != 3:
            raise ValueError(
                f"Not a Terraria player file: "
                f"{file_type}"
            )

        times_saved = reader.i32()

        favorite = reader.i64() != 0

        return {
            "times_saved": times_saved,
            "favorite": favorite,
        }

    def parse(self):
        data = self.decrypt()

        reader = BinaryReader(data)

        self.version = reader.i32()

        if self.version not in SUPPORTED_VERSIONS:
            raise ValueError(
                f"Unsupported Terraria player "
                f"version: {self.version}"
            )

        player = {
            "version": self.version,
        }

        version = self.version

        if version >= 135:
            header = self.read_player_header(
                reader
            )

            player.update(header)

        self.edit_offsets["name"] = reader.tell()

        player["name"] = reader.cs_string()

        player["difficulty"] = (
            self.read_difficulty(reader)
        )

        if version >= 138:
            ticks = reader.i64()

            player["playtime_ticks"] = ticks

            player["playtime_seconds"] = (
                ticks / 10000000
            )

        self.edit_offsets["hair_style"] = (
            reader.tell()
        )

        player["hair_style"] = reader.i32()

        if version >= 83:
            self.edit_offsets["hair_dye"] = (
                reader.tell()
            )

            player["hair_dye"] = reader.u8()
        else:
            player["hair_dye"] = None

        if version >= 283:
            self.edit_offsets["team"] = (
                reader.tell()
            )

            player["team"] = reader.u8()
        else:
            player["team"] = None

        if version >= 83:
            visibility = (
                reader.u16()
                if version >= 124
                else reader.u8()
            ) >> 3

            player["accessory_visibility"] = []

            for _ in range(7):
                player[
                    "accessory_visibility"
                ].append(
                    (visibility & 1) != 1
                )

                visibility >>= 1

        if version >= 119:
            byte = reader.u8()

            player["pet_visible"] = (
                byte & 1
            ) != 1

            player["light_pet_visible"] = (
                (byte >> 1) & 1
            ) != 1

        if version <= 17:
            player["style"] = (
                "FemaleStarter"
                if player["hair_style"]
                in (5, 6, 9, 11)
                else "MaleStarter"
            )

        elif version <= 107:
            player["style"] = (
                "MaleStarter"
                if reader.boolean()
                else "FemaleStarter"
            )

        else:
            style_id = reader.u8()

            player["style"] = {
                0: "MaleStarter",
                1: "MaleSticker",
                2: "MaleGangster",
                3: "MaleCoat",
                4: "FemaleStarter",
                5: "FemaleSticker",
                6: "FemaleGangster",
                7: (
                    "FemaleDress"
                    if version < 161
                    else "FemaleCoat"
                ),
                8: "MaleDress",
                9: "FemaleDress",
                10: "MaleDisplayDoll",
                11: "FemaleDisplayDoll",
            }.get(
                style_id,
                f"Unknown Style ({style_id})",
            )

        self.edit_offsets["life"] = reader.tell()

        player["life"] = reader.i32()

        self.edit_offsets["max_life"] = reader.tell()

        player["max_life"] = reader.i32()

        self.edit_offsets["mana"] = reader.tell()

        player["mana"] = reader.i32()

        self.edit_offsets["max_mana"] = reader.tell()

        player["max_mana"] = reader.i32()

        if version >= 125:
            player["demon_heart"] = reader.boolean()

        biome_torches_unlocked = False

        if version >= 229:
            biome_torches_unlocked = reader.boolean()

            reader.boolean()

        if version >= 256:
            player["artisan_bread"] = reader.boolean()

        if version >= 260:
            player["aegis_crystal"] = reader.boolean()
            player["aegis_fruit"] = reader.boolean()
            player["arcane_crystal"] = reader.boolean()
            player["galaxy_pearl"] = reader.boolean()
            player["gummy_worm"] = reader.boolean()
            player["ambrosia"] = reader.boolean()

        if version >= 182:
            player["dd2_event_downed"] = reader.boolean()

        if version >= 128:
            player["tax_money"] = reader.i32()

        if version >= 254:
            player[
                "deaths_not_caused_by_player"
            ] = reader.i32()

            player[
                "deaths_caused_by_player"
            ] = reader.i32()

        colors = [
            "hair",
            "skin",
            "eye",
            "shirt",
            "under_shirt",
            "pants",
            "shoe",
        ]

        player["colors"] = {}

        for color in colors:
            player["colors"][color] = (
                self.read_color(reader)
            )

        current_loadout = {
            "armor": [],
            "vanity": [],
            "dyes": [],
            "accessories": [],
        }

        for _ in range(3):
            current_loadout[
                "armor"
            ].append(
                self.read_single_item_slot(
                    reader
                )
            )

        for _ in range(
            7 if version >= 124 else 5
        ):
            current_loadout[
                "armor"
            ].append(
                self.read_single_item_slot(
                    reader
                )
            )

        if version >= 6:
            for _ in range(3):
                current_loadout[
                    "vanity"
                ].append(
                    self.read_single_item_slot(
                        reader
                    )
                )

        vanity_count = (
            0
            if version <= 80
            else 5
            if version <= 123
            else 7
        )

        for _ in range(vanity_count):
            current_loadout[
                "vanity"
            ].append(
                self.read_single_item_slot(
                    reader
                )
            )

        if version >= 47:
            for _ in range(3):
                current_loadout[
                    "dyes"
                ].append(
                    self.read_single_item_slot(
                        reader
                    )
                )

        dye_count = (
            0
            if version <= 80
            else 5
            if version <= 123
            else 7
        )

        for _ in range(dye_count):
            current_loadout[
                "dyes"
            ].append(
                self.read_single_item_slot(
                    reader
                )
            )

        player["inventory"] = (
            self.read_inventory(reader)
        )

        player["coins"] = (
            self.read_small_inventory(reader)
        )

        if version >= 15:
            player["ammo"] = (
                self.read_small_inventory(reader)
            )
        else:
            player["ammo"] = [None] * 4

        if version >= 136:
            player["pet"] = {
                "item":
                    self.read_single_item_slot(
                        reader
                    ),
                "dye":
                    self.read_single_item_slot(
                        reader
                    ),
            }

        if version >= 117:
            player["light_pet"] = {
                "item":
                    self.read_single_item_slot(
                        reader
                    ),
                "dye":
                    self.read_single_item_slot(
                        reader
                    ),
            }

            player["minecart"] = {
                "item":
                    self.read_single_item_slot(
                        reader
                    ),
                "dye":
                    self.read_single_item_slot(
                        reader
                    ),
            }

            player["mount"] = {
                "item":
                    self.read_single_item_slot(
                        reader
                    ),
                "dye":
                    self.read_single_item_slot(
                        reader
                    ),
            }

            player["hook"] = {
                "item":
                    self.read_single_item_slot(
                        reader
                    ),
                "dye":
                    self.read_single_item_slot(
                        reader
                    ),
            }

        player["piggy_bank"] = (
            self.read_container(reader)
        )

        if version >= 20:
            player["safe"] = (
                self.read_container(reader)
            )
        else:
            player["safe"] = None

        if version >= 182:
            player["defenders_forge"] = (
                self.read_container(reader)
            )
        else:
            player["defenders_forge"] = None

        player["void_vault"] = (
            self.read_void_vault(reader)
        )

        player["buffs"] = (
            self.read_buffs(reader)
        )

        player["spawn_points"] = (
            self.read_spawn_points(reader)
        )

        if version >= 16:
            player["hotbar_locked"] = (
                reader.boolean()
            )

        if version >= 115:
            player["info_visibility"] = {
                "time": not reader.boolean(),
                "weather": not reader.boolean(),
                "fishing_power": not reader.boolean(),
                "position": not reader.boolean(),
                "depth": not reader.boolean(),
                "creature_count": not reader.boolean(),
                "kill_count": not reader.boolean(),
                "moon_phase": not reader.boolean(),
            }

            reader.boolean()

            player[
                "info_visibility"
            ]["movement_speed"] = (
                not reader.boolean()
            )

            player[
                "info_visibility"
            ]["treasure_finder"] = (
                not reader.boolean()
            )

            player[
                "info_visibility"
            ]["rare_creatures_finder"] = (
                not reader.boolean()
            )

            player[
                "info_visibility"
            ]["damage_per_second"] = (
                not reader.boolean()
            )

            player[
                "angler_quests_completed"
            ] = reader.i32()

        if version >= 164:
            player["dpad_shortcuts"] = {
                "up": reader.i32(),
                "right": reader.i32(),
                "down": reader.i32(),
                "left": reader.i32(),
            }

            player[
                "ruler_enabled"
            ] = reader.i32() == 0

            player[
                "mechanical_ruler_enabled"
            ] = reader.i32() == 0

            player[
                "auto_paint_enabled"
            ] = reader.i32() == 0

            reader.i32()

            player[
                "red_wires_visibility"
            ] = self.read_visibility(reader)

            player[
                "blue_wires_visibility"
            ] = self.read_visibility(reader)

            player[
                "green_wires_visibility"
            ] = self.read_visibility(reader)

            player[
                "yellow_wires_visibility"
            ] = self.read_visibility(reader)

        if version >= 167:
            player[
                "always_show_wires_and_actuators"
            ] = reader.i32() == 0

            player[
                "actuators_visibility"
            ] = self.read_visibility(reader)

        if version >= 197:
            player[
                "tile_replacement_enabled"
            ] = reader.i32() == 0

        if version >= 230:
            biome_enabled = reader.i32() == 0

            player[
                "using_biome_torches"
            ] = (
                biome_enabled
                if biome_torches_unlocked
                else None
            )

        if version >= 181:
            player[
                "talked_to_bartender"
            ] = reader.i32() == 1

        if version >= 200:
            has_respawn = reader.boolean()

            if has_respawn:
                ticks = reader.i32()

                player[
                    "time_to_respawn_ticks"
                ] = ticks

                player[
                    "time_to_respawn_seconds"
                ] = ticks / 60.0
            else:
                player[
                    "time_to_respawn_ticks"
                ] = None

                player[
                    "time_to_respawn_seconds"
                ] = None

        if version >= 202:
            player[
                "last_saved_ticks"
            ] = reader.i64()

        if version >= 206:
            player[
                "golfer_score"
            ] = reader.i32()

        if version >= 282:
            reader.boolean()

        if version >= 218:
            count = max(
                reader.i32(),
                0,
            )

            researched = {}

            for _ in range(count):
                code_name = reader.cs_string()

                amount = reader.i32()

                researched[code_name] = amount

            player["researched_items"] = researched

        if version >= 214:
            flags = reader.u8()

            player["temporary_items"] = {}

            if flags & 1:
                player[
                    "temporary_items"
                ]["mouse"] = (
                    self.read_item_slot(reader)
                )

            if flags >> 1 & 1:
                player[
                    "temporary_items"
                ]["research"] = (
                    self.read_item_slot(reader)
                )

            if flags >> 2 & 1:
                player[
                    "temporary_items"
                ]["guide"] = (
                    self.read_item_slot(reader)
                )

            if flags >> 3 & 1:
                player[
                    "temporary_items"
                ]["goblin"] = (
                    self.read_item_slot(reader)
                )

        if version >= 220:
            player["journey_settings"] = {}

            while reader.boolean():
                key = reader.i16()

                if key == 5:
                    player[
                        "journey_settings"
                    ]["godmode"] = (
                        reader.boolean()
                    )

                elif key == 11:
                    player[
                        "journey_settings"
                    ]["far_placement"] = (
                        reader.boolean()
                    )

                elif key == 14:
                    player[
                        "journey_settings"
                    ]["spawn_rate"] = (
                        reader.f32()
                    )

        if version >= 253:
            value = reader.u8()

            if value & 1:
                player[
                    "super_cart_enabled"
                ] = (
                    value & 2
                ) != 0
            else:
                player[
                    "super_cart_enabled"
                ] = None

        if version >= 262:
            player["loadouts"] = (
                self.read_loadouts(
                    reader,
                    current_loadout,
                )
            )
        else:
            player["loadouts"] = None

        if version >= 280:
            player["voice"] = reader.u8()
        else:
            player["voice"] = None

        if version >= 281:
            player[
                "voice_pitch_offset"
            ] = reader.f32()

        if version >= 300:
            count = max(
                reader.i32(),
                0,
            )

            refunds = []

            for _ in range(count):
                item = self.read_item_slot(
                    reader
                )

                if item is not None:
                    refunds.append(item)

            player["refunds"] = refunds

        if version >= 310:
            count = max(
                reader.i32(),
                0,
            )

            dialogues = []

            for _ in range(count):
                dialogues.append(
                    reader.cs_string()
                )

            player[
                "one_time_dialogues_seen"
            ] = dialogues

        player["_parser_offset"] = reader.tell()

        player["_remaining_bytes"] = (
            reader.remaining()
        )

        return player