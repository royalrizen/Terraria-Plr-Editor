# Terraria Player / Plr Editor

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
![License](https://img.shields.io/github/license/royalrizen/Terraria-Plr-Editor?style=flat)
![GitHub Stars](https://img.shields.io/github/stars/royalrizen/Terraria-Plr-Editor?style=flat)
![GitHub Issues](https://img.shields.io/github/issues/royalrizen/Terraria-Plr-Editor?style=flat)

A lightweight Python library and CLI for reading, inspecting, and editing Terraria `.plr` player files.
Terraria Player Editor handles the underlying encryption and binary format, allowing player data to be accessed through a clean Python API instead of manually working with raw bytes. It includes a version-aware parser, bundled item database, inventory support, and an editor for supported player properties and inventory values.

It can be used either as a **standalone command-line tool** or integrated directly into your own Python projects.

<br>

> [!NOTE]
> Terraria is developed by **Re-Logic**. This project is an independent community tool and is not affiliated with or endorsed by Re-Logic.

<br>


## 🎗️ Features

| Feature | Description |
|---|---|
| 🔐 **Encryption** | Automatically decrypt and re-encrypt Terraria player files |
| 📖 **Player Parser** | Parse supported Terraria `.plr` file versions |
| 🎒 **Inventory** | Read items, quantities, prefixes, and favorite states |
| 🧍 **Player Data** | Access character information, stats, difficulty, and other parsed data |
| ✏️ **Player Editor** | Modify supported player properties and inventory slots |
| 🗃️ **Item Database** | Resolve Terraria item IDs using the bundled database |
| 🖥️ **CLI** | Inspect and edit player files directly from the terminal |
| 🐍 **Python API** | Integrate the parser and editor into your own projects |
| 💾 **Save** | Save edited data back into an encrypted `.plr` file |

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/royalrizen/Terraria-Plr-Editor.git
cd Terraria-Plr-Editor
```

Install the package:

```bash
pip install .
```

For development:

```bash
pip install -e .
```

## 🖥️ CLI Usage

After installation, the `terraria-player` command is available globally.

### Help

```bash
terraria-player --help
```

### Player information

```bash
terraria-player info player.plr
```

### Inventory

```bash
terraria-player inventory player.plr
```

### All parsed data

```bash
terraria-player all player.plr
```

The bundled `data/items.json` database is handled internally, so you **do not need to provide an `--items` argument**.

### Editing

```bash
terraria-player edit player.plr
```

The editor provides access to the supported player and inventory modifications.

Edited player files are saved separately, with the original file preserved as a `.bak` backup when applicable.

---

## 🐍 Python API

The parser and editor can also be used directly from Python.

### Parse a player

```python
from terraria_player import PlayerParser

parser = PlayerParser(
    "player.plr",
    "data/items.json",
)

player = parser.parse()

print(player["name"])
print(player["life"])
print(player["max_life"])
```

### Read inventory

```python
from terraria_player import PlayerParser

parser = PlayerParser(
    "player.plr",
    "data/items.json",
)

player = parser.parse()

for row, slots in enumerate(player["inventory"]):
    for slot, item in enumerate(slots):
        if item is None:
            continue

        print(
            f"[{row}:{slot}] "
            f"{item.name} "
            f"(ID {item.id}) "
            f"x{item.count}"
        )
```

### Edit a player

```python
from terraria_player import PlayerParser, PlayerEditor

parser = PlayerParser(
    "player.plr",
    "data/items.json",
)

parser.parse()

editor = PlayerEditor(parser)

editor.set_name("My Character")
editor.set_life(400)
editor.set_max_life(400)

editor.save("edited.plr")
```

### Edit an inventory slot

```python
editor.set_inventory_item(
    row=0,
    slot=0,
    count=99,
)
```

Supported inventory fields can also be changed together:

```python
editor.set_inventory_item(
    row=0,
    slot=0,
    item_id=9,
    count=99,
    prefix=0,
    favorite=True,
)
```

---

## 📚 API

### `PlayerParser`

| Method | Description |
|---|---|
| `parse()` | Parse the player file |
| `decrypt()` | Decrypt the player file |
| `read_inventory()` | Read the main inventory |
| `read_loadouts()` | Read player loadouts |
| `read_buffs()` | Read active buffs |
| `read_spawn_points()` | Read spawn points |

### `PlayerEditor`

| Method | Description |
|---|---|
| `set_name()` | Change the player name |
| `set_hair_style()` | Change the hair style |
| `set_hair_dye()` | Change the hair dye |
| `set_team()` | Change the team |
| `set_life()` | Change current life |
| `set_max_life()` | Change maximum life |
| `set_mana()` | Change current mana |
| `set_max_mana()` | Change maximum mana |
| `set_inventory_item()` | Modify an inventory slot |
| `save()` | Save the edited player file |

---

## 📁 Project Structure

```text
Terraria-Plr-Editor/
├── data/
│   └── items.json
├── src/
│   └── terraria_player/
│       ├── binary/
│       ├── cli/
│       ├── crypto/
│       ├── database/
│       ├── editor/
│       ├── models/
│       └── parser/
├── pyproject.toml
└── README.md
```

<br>

## 🤝 Contributing

Contributions are always welcome.

If you have a bug fix, improvement, or new idea:

1. Fork the repository
2. Create a branch for your changes
3. Make and test your changes
4. Open a pull request with a clear description

For larger changes to the parser or player format, please open an issue first so the approach can be discussed.

### 🐛 Bugs & Ideas

Found a bug or have a feature idea?

[Open an issue →](https://github.com/royalrizen/Terraria-Plr-Editor/issues/new)

When reporting a bug, include the relevant Terraria/player-file version, Python version, error message, and steps to reproduce it.

> [!WARNING]
> Please don't upload personal `.plr` files to public issues.

---

## 📜 License

This project is under the [MIT LICENSE](LICENSE).

## ✨ Credits

- **[@royalrizen](https://github.com/royalrizen)**

<p align="center">
  <sub>Built for the Terraria Community · Made with ♥️</sub>
</p>
