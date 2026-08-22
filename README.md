<p align="center">
  <img src="https://i.ibb.co/KjWz408y/Untitled45-20260820132906.png" alt="Terraria Player Editor">
</p>

<h1 align="center">Terraria Player / .plr Editor (1.4.5.6) </h1>

<p align="center">
  A lightweight Python library and CLI for reading, inspecting, and editing Terraria player files.
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/royalrizen/Terraria-Plr-Editor?style=flat&color=green" alt="Stars">
  <img src="https://img.shields.io/github/issues/royalrizen/Terraria-Plr-Editor?style=flat" alt="Issues">
  <img src="https://img.shields.io/github/license/royalrizen/Terraria-Plr-Editor?style=flat" alt="License">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white" alt="Python">
</p>

<br>

## About

**Terraria Player Editor** is a Python library and command-line tool for working with Terraria `.plr` player files.

It handles the underlying player-file encryption and binary data, providing a higher-level interface for inspecting player information, inventories, and supported character properties. The project includes a version-aware parser, a bundled Terraria item database, and an editor for modifying supported values before saving them back to a player file.

The project can be used directly through the **CLI** or imported as a **Python package** for integration into other applications, scripts, or tools.

> [!NOTE]
> Terraria is developed by **Re-Logic**. This is an independent community project and is not affiliated with or endorsed by Re-Logic.

---

## 🎗️ Features

| Feature | Description |
|---|---|
| 🔐 **Encryption** | Automatically decrypts and re-encrypts `.plr` files |
| 📖 **Parser** | Parses supported Terraria player-file versions |
| 🎒 **Inventory** | Reads item IDs, names, quantities, prefixes, and favorite states |
| 🧍 **Player Data** | Accesses parsed character information and statistics |
| ✏️ **Editor** | Modifies supported player properties and inventory values |
| 🗃️ **Item Database** | Includes a bundled `items.json` database |
| 🖥️ **CLI** | Provides a simple terminal interface |
| 🐍 **Python API** | Use the parser and editor directly from Python |
| 💾 **Save** | Saves edited player data back into an encrypted `.plr` file |

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

The package includes the item database, so no separate `items.json` argument is required.

---

## 🖥️ CLI

After installation, use the `terraria-player` command.

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

### Editing

```bash
terraria-player edit player.plr
```

The CLI automatically locates the bundled item database.

---

## 🐍 Python API

The parser can be used directly in your own project:

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

### Reading inventory

```python
for row_index, row in enumerate(player["inventory"]):
    for slot_index, item in enumerate(row):
        if item is None:
            continue

        print(
            f"[{row_index}:{slot_index}] "
            f"{item.name} ×{item.count}"
        )
```

### Editing a player

```python
from terraria_player import PlayerParser, PlayerEditor

parser = PlayerParser(
    "player.plr",
    "data/items.json",
)

editor = PlayerEditor(parser)

editor.set_name("Rizen")
editor.set_life(200)
editor.set_max_life(400)

editor.save("edited_player.plr")
```

Inventory values can also be modified:

```python
editor.set_inventory_item(
    row=0,
    slot=0,
    count=99,
)
```

---

## 📚 API

### PlayerParser

| Method | Description |
|---|---|
| `parse()` | Parse the player file |
| `decrypt()` | Decrypt the player file |
| `read_inventory()` | Read the main inventory |
| `read_loadouts()` | Read player loadouts |
| `read_buffs()` | Read active buffs |
| `read_spawn_points()` | Read spawn points |

### PlayerEditor

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

## 🤝 Contributing

Contributions are welcome.

If you have a bug fix, improvement, or useful feature:

1. Fork the repository.
2. Create a branch for your change.
3. Make your changes.
4. Test them with a Terraria `.plr` file.
5. Open a pull request with a clear description.

```bash
git checkout -b feature/my-change
```

For larger parser or file-format changes, opening an issue first is recommended.

### 🐛 Bug Reports

Please include:

- Terraria/player-file version
- Python version
- Command or code used
- Full error message
- Steps to reproduce the issue

> [!WARNING]
> Please do not upload personal `.plr` files publicly.

### 💡 Feature Requests

Have an idea?

[Open an issue](https://github.com/royalrizen/Terraria-Plr-Editor/issues/new) and describe what you'd like to see and why it would be useful.

---

## 📜 License

This project is licensed under the **MIT License**.
See [LICENSE](LICENSE) for the full license text.

---

## ✨ Credits

Created and maintained by **[@royalrizen](https://github.com/royalrizen)**.

<p align="center">
  <sub>Made with ♥️ · For Terraria Community</sub>
</p>
