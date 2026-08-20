from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from terraria_player import PlayerParser
from terraria_player.editor.player import PlayerEditor


RESET = "\033[0m"
BOLD = "\033[1m"

GREEN = "\033[92m"
CYAN = "\033[96m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
RED = "\033[91m"
WHITE = "\033[97m"
GRAY = "\033[90m"


LOGO = f"""{GREEN}{BOLD}
████████╗███████╗██████╗ ██████╗  █████╗ ██████╗ ██╗ █████╗
╚══██╔══╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗██║██╔══██╗
   ██║   █████╗  ██████╔╝██████╔╝██████╔╝██████╔╝██║███████║
   ██║   ██╔══╝  ██╔══██╗██╔══██╗██╔══██║██╔══██╗██║██╔══██║
   ██║   ███████╗██║  ██║██║  ██║██║  ██║██║  ██║██║██║  ██║
   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝
                     PLAYER EDITOR
{RESET}"""


def terminal_width() -> int:
    return shutil.get_terminal_size((80, 24)).columns


def print_logo() -> None:
    print(LOGO)


def visible_length(text: str) -> int:
    import re

    return len(
        re.sub(
            r"\033\[[0-9;]*m",
            "",
            text,
        )
    )


def box(
    title: str,
    lines: list[str],
    minimum_width: int = 38,
) -> None:
    content_width = max(
        visible_length(title) + 4,
        *(visible_length(line) + 4 for line in lines),
        minimum_width - 2,
    )

    width = min(
        max(content_width + 2, minimum_width),
        terminal_width(),
    )

    print(
        f"{GREEN}╭"
        f"{'─' * (width - 2)}"
        f"╮{RESET}"
    )

    title_padding = width - visible_length(title) - 4

    print(
        f"{GREEN}│{RESET}  "
        f"{BOLD}{WHITE}{title}{RESET}"
        f"{' ' * max(0, title_padding)}"
        f"{GREEN}│{RESET}"
    )

    print(
        f"{GREEN}╰"
        f"{'─' * (width - 2)}"
        f"╯{RESET}"
    )

    for line in lines:
        print(f"  {line}")


def section(title: str) -> None:
    width = min(terminal_width(), 70)

    print()
    print(
        f"{GREEN}── {BOLD}{title}{RESET}"
        f"{GREEN} "
        f"{'─' * max(0, width - len(title) - 4)}"
        f"{RESET}"
    )


def pause() -> None:
    input(
        f"\n{GRAY}Press Enter to continue...{RESET}"
    )


def ask(prompt: str) -> str:
    return input(
        f"{GREEN}>{RESET} {prompt}"
    ).strip()


def ask_int(
    prompt: str,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    while True:
        value = ask(prompt)

        try:
            value = int(value)
        except ValueError:
            print(
                f"{RED}✖ Enter a valid number.{RESET}"
            )
            continue

        if minimum is not None and value < minimum:
            print(
                f"{RED}✖ Minimum: {minimum}{RESET}"
            )
            continue

        if maximum is not None and value > maximum:
            print(
                f"{RED}✖ Maximum: {maximum}{RESET}"
            )
            continue

        return value


def confirm(prompt: str) -> bool:
    while True:
        value = ask(
            f"{prompt} [y/n]"
        ).lower()

        if value in ("y", "yes"):
            return True

        if value in ("n", "no"):
            return False

        print(
            f"{RED}✖ Please enter y or n.{RESET}"
        )


def get_items_path() -> Path:
    current = Path(__file__).resolve()

    candidates = []

    for parent in current.parents:
        candidates.append(
            parent / "data" / "items.json"
        )

    for path in candidates:
        if path.exists():
            return path

    raise FileNotFoundError(
        "Bundled item database not found. "
        "Expected project/data/items.json."
    )


def load_parser(player_file: Path):
    items_file = get_items_path()

    if not player_file.exists():
        raise FileNotFoundError(
            f"Player file not found: {player_file}"
        )

    parser = PlayerParser(
        player_file=player_file,
        items_file=items_file,
    )

    parser.parse()

    return parser


def load_player(player_file: Path):
    parser = load_parser(player_file)
    return parser.parse()


def print_player_info(player: dict) -> None:
    lines = [
        f"{GREEN}Name{RESET}        │ {WHITE}{player['name']}{RESET}",
        f"{GREEN}Version{RESET}     │ {WHITE}{player['version']}{RESET}",
        f"{GREEN}Difficulty{RESET}  │ {YELLOW}{player['difficulty']}{RESET}",
    ]

    if player.get("playtime_seconds") is not None:
        hours = player["playtime_seconds"] / 3600

        lines.append(
            f"{GREEN}Playtime{RESET}    │ "
            f"{WHITE}{hours:.1f} hours{RESET}"
        )

    box("PLAYER", lines)


def print_stats(player: dict) -> None:
    section("STATS")

    print(
        f"  {RED}♥{RESET} "
        f"{WHITE}Life{RESET} "
        f"{player['life']} / {player['max_life']}"
    )

    print(
        f"  {BLUE}✦{RESET} "
        f"{WHITE}Mana{RESET} "
        f"{player['mana']} / {player['max_mana']}"
    )


def print_character(player: dict) -> None:
    section("CHARACTER")

    print(
        f"  {CYAN}Hair Style{RESET} │ "
        f"{player['hair_style']}"
    )

    print(
        f"  {CYAN}Style{RESET}      │ "
        f"{player['style']}"
    )

    print(
        f"  {CYAN}Hair Dye{RESET}   │ "
        f"{player['hair_dye']}"
    )

    if player.get("team") is not None:
        print(
            f"  {CYAN}Team{RESET}       │ "
            f"{player['team']}"
        )


def inventory_lines(inventory) -> list[str]:
    lines = []

    for row_index, row in enumerate(inventory):
        for slot_index, item in enumerate(row):
            if item is None:
                continue

            favorite = (
                f" {YELLOW}★{RESET}"
                if item.favorite
                else ""
            )

            lines.append(
                f"{GRAY}[{row_index}:{slot_index}]{RESET} "
                f"{WHITE}{item.name}{RESET} "
                f"{GREEN}×{item.count}{RESET} "
                f"{GRAY}ID:{item.id}{RESET}"
                f"{favorite}"
            )

            if item.prefix:
                lines.append(
                    f"        "
                    f"{MAGENTA}Prefix: {item.prefix}{RESET}"
                )

    return lines


def print_inventory(
    title: str,
    inventory,
) -> None:
    lines = inventory_lines(inventory)

    if not lines:
        lines = [
            f"{GRAY}Empty{RESET}"
        ]

    box(
        title,
        lines,
        minimum_width=30,
    )


def print_parser_info(player: dict) -> None:
    section("PARSER")

    print(
        f"  {GRAY}Final Offset{RESET}    │ "
        f"{player['_parser_offset']}"
    )

    print(
        f"  {GRAY}Remaining Bytes{RESET} │ "
        f"{player['_remaining_bytes']}"
    )


def print_footer() -> None:
    width = min(
        terminal_width(),
        70,
    )

    print()
    print(
        f"{GRAY}{'─' * width}{RESET}"
    )
    print(
        f"{GRAY}  Terraria Player Editor{RESET}"
    )
    print(
        f"{GRAY}  Made by {GREEN}@royalrizen"
        f"{GRAY} on {GREEN}GitHub{RESET}"
    )
    print(
        f"{GRAY}{'─' * width}{RESET}"
    )


def command_info(args) -> None:
    print_logo()

    player = load_player(args.player)

    print_player_info(player)
    print_stats(player)
    print_character(player)

    print_footer()


def command_inventory(args) -> None:
    print_logo()

    player = load_player(args.player)

    print_inventory(
        "INVENTORY",
        player["inventory"],
    )

    print_footer()


def command_all(args) -> None:
    print_logo()

    player = load_player(args.player)

    print_player_info(player)
    print_stats(player)
    print_character(player)

    print_inventory(
        "INVENTORY",
        player["inventory"],
    )

    print_inventory(
        "COINS",
        [player["coins"]],
    )

    print_inventory(
        "AMMO",
        [player["ammo"]],
    )

    print_inventory(
        "PIGGY BANK",
        player["piggy_bank"],
    )

    if player["safe"] is not None:
        print_inventory(
            "SAFE",
            player["safe"],
        )

    if player["defenders_forge"] is not None:
        print_inventory(
            "DEFENDERS FORGE",
            player["defenders_forge"],
        )

    if player["void_vault"] is not None:
        print_inventory(
            "VOID VAULT",
            player["void_vault"],
        )

    print_parser_info(player)
    print_footer()


def edit_player_menu(
    editor: PlayerEditor,
    player: dict,
) -> None:
    while True:
        print()
        box(
            "PLAYER EDITOR",
            [
                f"{GRAY}Player{RESET}     : "
                f"{WHITE}{player['name']}{RESET}",
                f"{GRAY}Version{RESET}    : "
                f"{player['version']}",
                "",
                f"{GREEN}1{RESET}  Player",
                f"{GREEN}2{RESET}  Stats",
                f"{GREEN}3{RESET}  Inventory",
                f"{GREEN}4{RESET}  Save",
                "",
                f"{GREEN}0{RESET}  Exit",
            ],
            minimum_width=42,
        )

        choice = ask("Select")

        if choice == "1":
            edit_character_menu(
                editor,
                player,
            )

        elif choice == "2":
            edit_stats_menu(
                editor,
                player,
            )

        elif choice == "3":
            edit_inventory_menu(
                editor,
                player,
            )

        elif choice == "4":
            return

        elif choice == "0":
            return

        else:
            print(
                f"{RED}✖ Invalid option.{RESET}"
            )


def edit_character_menu(
    editor: PlayerEditor,
    player: dict,
) -> None:
    while True:
        print()
        box(
            "PLAYER",
            [
                f"{GREEN}1{RESET}  Name        "
                f"{WHITE}{player['name']}{RESET}",
                f"{GREEN}2{RESET}  Hair Style  "
                f"{player['hair_style']}",
                f"{GREEN}3{RESET}  Hair Dye    "
                f"{player['hair_dye']}",
                f"{GREEN}4{RESET}  Team        "
                f"{player.get('team', 'N/A')}",
                "",
                f"{GREEN}0{RESET}  Back",
            ],
            minimum_width=42,
        )

        choice = ask("Select")

        try:
            if choice == "1":
                name = ask("New name")

                if name:
                    editor.set_name(name)
                    player["name"] = name

            elif choice == "2":
                value = ask_int(
                    "Hair style",
                    0,
                )

                editor.set_hair_style(value)
                player["hair_style"] = value

            elif choice == "3":
                value = ask_int(
                    "Hair dye",
                    0,
                    255,
                )

                editor.set_hair_dye(value)
                player["hair_dye"] = value

            elif choice == "4":
                if editor.version < 283:
                    print(
                        f"{YELLOW}Team is not "
                        f"available in this version.{RESET}"
                    )
                    continue

                value = ask_int(
                    "Team",
                    0,
                    5,
                )

                editor.set_team(value)
                player["team"] = value

            elif choice == "0":
                return

            else:
                print(
                    f"{RED}✖ Invalid option.{RESET}"
                )

        except (ValueError, TypeError) as exc:
            print(
                f"{RED}✖ {exc}{RESET}"
            )


def edit_stats_menu(
    editor: PlayerEditor,
    player: dict,
) -> None:
    while True:
        print()
        box(
            "STATS",
            [
                f"{GREEN}1{RESET}  Life      "
                f"{WHITE}{player['life']}{RESET}",
                f"{GREEN}2{RESET}  Max Life  "
                f"{WHITE}{player['max_life']}{RESET}",
                f"{GREEN}3{RESET}  Mana      "
                f"{WHITE}{player['mana']}{RESET}",
                f"{GREEN}4{RESET}  Max Mana  "
                f"{WHITE}{player['max_mana']}{RESET}",
                "",
                f"{GREEN}0{RESET}  Back",
            ],
            minimum_width=42,
        )

        choice = ask("Select")

        try:
            if choice == "1":
                value = ask_int(
                    "Life",
                    0,
                )

                editor.set_life(value)
                player["life"] = value

            elif choice == "2":
                value = ask_int(
                    "Max life",
                    0,
                )

                editor.set_max_life(value)
                player["max_life"] = value

            elif choice == "3":
                value = ask_int(
                    "Mana",
                    0,
                )

                editor.set_mana(value)
                player["mana"] = value

            elif choice == "4":
                value = ask_int(
                    "Max mana",
                    0,
                )

                editor.set_max_mana(value)
                player["max_mana"] = value

            elif choice == "0":
                return

            else:
                print(
                    f"{RED}✖ Invalid option.{RESET}"
                )

        except (ValueError, TypeError) as exc:
            print(
                f"{RED}✖ {exc}{RESET}"
            )


def find_inventory_item(
    player: dict,
    row: int,
    slot: int,
):
    inventory = player["inventory"]

    if not 0 <= row < len(inventory):
        return None

    if not 0 <= slot < len(inventory[row]):
        return None

    return inventory[row][slot]


def edit_inventory_slot(
    editor: PlayerEditor,
    player: dict,
    row: int,
    slot: int,
) -> None:
    item = find_inventory_item(
        player,
        row,
        slot,
    )

    if item is None:
        print(
            f"{YELLOW}Slot is empty.{RESET}"
        )
        return

    while True:
        print()

        favorite = (
            f"{GREEN}Yes{RESET}"
            if item.favorite
            else f"{GRAY}No{RESET}"
        )

        box(
            f"EDIT [{row}:{slot}]",
            [
                f"{GREEN}Item{RESET}      │ "
                f"{WHITE}{item.name}{RESET}",
                f"{GREEN}ID{RESET}        │ "
                f"{item.id}",
                f"{GREEN}Count{RESET}     │ "
                f"{item.count}",
                f"{GREEN}Prefix{RESET}    │ "
                f"{item.prefix}",
                f"{GREEN}Favorite{RESET}  │ "
                f"{favorite}",
                "",
                f"{GREEN}1{RESET}  Change item ID",
                f"{GREEN}2{RESET}  Change count",
                f"{GREEN}3{RESET}  Change prefix",
                f"{GREEN}4{RESET}  Toggle favorite",
                "",
                f"{GREEN}0{RESET}  Back",
            ],
            minimum_width=44,
        )

        choice = ask("Select")

        try:
            if choice == "1":
                item_id = ask_int(
                    "Item ID",
                    1,
                )

                editor.set_inventory_item(
                    row,
                    slot,
                    item_id=item_id,
                )

                item.id = item_id

                database_item = (
                    editor.parser.items.get(
                        item_id
                    )
                )

                if database_item is not None:
                    item.name = database_item.get(
                        "name",
                        item.name,
                    )

                print(
                    f"{GREEN}✔ Item changed.{RESET}"
                )

            elif choice == "2":
                count = ask_int(
                    "Count",
                    0,
                )

                editor.set_inventory_item(
                    row,
                    slot,
                    count=count,
                )

                item.count = count

                if count == 0:
                    player["inventory"][row][slot] = None
                    print(
                        f"{GREEN}✔ Item removed.{RESET}"
                    )
                    return

            elif choice == "3":
                prefix = ask_int(
                    "Prefix",
                    0,
                    255,
                )

                editor.set_inventory_item(
                    row,
                    slot,
                    prefix=prefix,
                )

                item.prefix = prefix

            elif choice == "4":
                new_value = not item.favorite

                editor.set_inventory_item(
                    row,
                    slot,
                    favorite=new_value,
                )

                item.favorite = new_value

            elif choice == "0":
                return

            else:
                print(
                    f"{RED}✖ Invalid option.{RESET}"
                )

        except (
            ValueError,
            TypeError,
            IndexError,
            NotImplementedError,
        ) as exc:
            print(
                f"{RED}✖ {exc}{RESET}"
            )


def edit_inventory_menu(
    editor: PlayerEditor,
    player: dict,
) -> None:
    while True:
        print()
        print_inventory(
            "INVENTORY",
            player["inventory"],
        )

        print()
        print(
            f"  {GREEN}e{RESET}  Edit slot"
        )
        print(
            f"  {GREEN}0{RESET}  Back"
        )

        choice = ask("Select").lower()

        if choice == "e":
            row = ask_int(
                "Row",
                0,
                len(player["inventory"]) - 1,
            )

            slot = ask_int(
                "Slot",
                0,
                len(player["inventory"][row]) - 1,
            )

            edit_inventory_slot(
                editor,
                player,
                row,
                slot,
            )

        elif choice == "0":
            return

        else:
            print(
                f"{RED}✖ Invalid option.{RESET}"
            )


def command_edit(args) -> None:
    print_logo()

    parser = load_parser(args.player)

    player = parser.parse()

    editor = PlayerEditor(parser)

    edit_player_menu(
        editor,
        player,
    )

    if not confirm(
        "Save changes?"
    ):
        print(
            f"{YELLOW}Changes discarded.{RESET}"
        )
        return

    output = args.output

    if output is None:
        output = args.player

    output = Path(output)

    if output == args.player and args.backup:
        backup = output.with_suffix(
            output.suffix + ".bak"
        )

        backup.write_bytes(
            output.read_bytes()
        )

        print(
            f"{GREEN}✔ Backup created:{RESET} "
            f"{backup}"
        )

    editor.save(output)

    print(
        f"{GREEN}{BOLD}✔ Player saved!{RESET}"
    )

    print(
        f"  {GRAY}{output}{RESET}"
    )

    print_footer()


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="terraria-player",
        description=(
            "Inspect and edit Terraria "
            "player (.plr) files."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  terraria-player info player.plr

  terraria-player inventory player.plr

  terraria-player all player.plr

  terraria-player edit player.plr

  terraria-player edit player.plr --output edited.plr
""",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    info = subparsers.add_parser(
        "info",
        help="Show player information.",
    )

    info.add_argument(
        "player",
        type=Path,
    )

    info.set_defaults(
        func=command_info,
    )

    inventory = subparsers.add_parser(
        "inventory",
        help="Show player inventory.",
    )

    inventory.add_argument(
        "player",
        type=Path,
    )

    inventory.set_defaults(
        func=command_inventory,
    )

    all_command = subparsers.add_parser(
        "all",
        help="Show all parsed player data.",
    )

    all_command.add_argument(
        "player",
        type=Path,
    )

    all_command.set_defaults(
        func=command_all,
    )

    edit = subparsers.add_parser(
        "edit",
        help="Interactively edit a player.",
    )

    edit.add_argument(
        "player",
        type=Path,
        help="Path to the .plr file.",
    )

    edit.add_argument(
        "--output",
        "-o",
        type=Path,
        help=(
            "Output .plr file. "
            "Defaults to replacing the original."
        ),
    )

    edit.add_argument(
        "--no-backup",
        dest="backup",
        action="store_false",
        help="Do not create a .bak backup.",
    )

    edit.set_defaults(
        func=command_edit,
        backup=True,
    )

    return parser


def main() -> int:
    parser = create_parser()
    args = parser.parse_args()

    try:
        args.func(args)

    except KeyboardInterrupt:
        print(
            f"\n{YELLOW}Cancelled.{RESET}",
            file=sys.stderr,
        )
        return 130

    except (
        FileNotFoundError,
        ValueError,
    ) as exc:
        print(
            f"\n{RED}✖ Error:{RESET} {exc}",
            file=sys.stderr,
        )
        return 1

    except Exception as exc:
        print(
            f"\n{RED}✖ Unexpected error:{RESET} {exc}",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())