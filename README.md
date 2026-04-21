# Logos to Markdown Export

This script automates the export of **Logos Bible Software** Notes and Sermons to Markdown files, compatible with applications like **Obsidian**, **Logseq**, or **Zettlr**.

## Features
- **Notes:** Exports your notes organized by Notebooks.
- **Sermons:** Exports your sermons from the Sermon Builder.
- **Formatting:** Preserves basic bold, italic, and metadata (YAML frontmatter).
- **Internationalization:** Automatically detects system language (EN or PT-BR) for messages and folder names.

## Prerequisites

To run this script, you need to have **Python 3** installed on your computer.

### How to install Python

#### On Windows:
1. Go to [python.org](https://www.python.org/downloads/).
2. Click the download button for the latest version.
3. **Important:** During installation, check the box **"Add Python to PATH"**.
4. Follow the instructions to completion.

#### On Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3
```

## How to Use

1. Download the `logos_to_markdown.py` file.
2. Open your terminal or command prompt in the folder where the file is located.
3. Run the script:

```bash
python3 logos_to_markdown.py --output Logos_Vault
```

### Where is the Logos directory?

The script tries to automatically detect the Logos path. If it fails, you will need to provide it manually using the `--logos-path` parameter.

#### On Windows:
It is usually located at:
`C:\Users\YOUR_USER\AppData\Local\Logos`

Example command:
```bash
python3 logos_to_markdown.py --logos-path "C:\Users\Username\AppData\Local\Logos" --output MyNotes
```

#### On Linux:
If you use the `oudedetai` script from FaithLife-Community, the path is usually something like:
`~/.local/share/FaithLife-Community/oudedetai/data/wine64_bottle/drive_c/users/YOUR_USER/AppData/Local/Logos`

Example command:
```bash
python3 logos_to_markdown.py --logos-path "/path/to/logos" --output Logos_Vault
```

## Available Parameters

- `--logos-path` or `-l`: Manual path to the Logos folder.
- `--output` or `-o`: Name of the destination folder for the `.md` files (Default: `Logos_Vault`).

## Important Note
This script accesses Logos' local SQLite databases in read-only mode. Make sure Logos is closed when running the script to avoid database access conflicts.
