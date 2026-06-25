# RafikOne CLI

A professional terminal-based quotation manager for Ubuntu Linux.

Typing `rafikone` opens an interactive dashboard. Typing `rafikone <command>` runs commands directly — both modes share the same business logic.

## Features

- **Interactive Dashboard** — Rich TUI with keyboard navigation, live search, and nested screens
- **Command Mode** — All 17 CLI commands work directly for scripting and quick access
- **Quotation Management** — Create, search, list, and organize quotations
- **Auto-numbering** — Global sequential quotation numbers (QTN-0001, QTN-0002, ...)
- **Folder Automation** — Creates structured folders and blank placeholder PDFs
- **Health Checks** — Doctor command validates your quotation structure

## Quick Start

```bash
# Install
pip install rafikone-cli

# Configure
rafikone init
# Enter your project root path (e.g., /home/user/Documents/Billionaire Homes)

# Launch dashboard
rafikone

# Or use commands directly
rafikone new
rafikone list
rafikone search akash
rafikone info 0034
rafikone open 0034
```

## Commands

| Command | Description |
|---|---|
| `init` | Set up project root directory |
| `config` | Display or update configuration |
| `new` | Create a new quotation (interactive) |
| `next` | Show latest and next quotation numbers |
| `list` | List all quotations (`--detailed`, `--site`, `--date`) |
| `recent` | Display 10 most recent quotations |
| `today` | Display today's quotations |
| `search` | Search by number, site name, or date |
| `info` | Detailed quotation info with folder stats |
| `open` | Open quotation folder in file manager |
| `invoice` | Open Invoices folder |
| `payment` | Open Payments folder |
| `challan` | Open Challans folder |
| `photos` | Open Site_Photos folder |
| `tree` | Display folder tree |
| `stats` | Show statistics |
| `doctor` | Check structure for issues |

## Dashboard

```
rafikone
```

Launches a full-screen TUI with:

- Keyboard navigation (↑↓ Enter Esc)
- Live fuzzy search
- Quotation details with actions (open folder, open PDF, etc.)
- Statistics panel
- Settings and Help screens

## Folder Structure

```
Project/
└── Quotations/
    └── Site_Name/
        └── YYYY-MM-DD/
            └── QTN-0001/
                ├── Invoices/
                ├── Payments/
                ├── Challans/
                ├── Site_Photos/
                └── SITE_QTN-0001_YYYY-MM-DD.pdf
```

## License

MIT
