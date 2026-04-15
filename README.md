# log-viewer

A GTK log viewer for the systemd journal (Linux only).

## Requirements

- Linux with systemd and journalctl (systemd 219+, shipped with most modern distros — Ubuntu 15.04+, Fedora 21+, Debian 8+, Arch, etc.; **not** available on Alpine, Void, or other non-systemd distros)
- Python 3.10+
- GTK 3 with Python GObject bindings (`python3-gi` / `gir1.2-gtk-3.0`)
- A graphical environment (X11 or Wayland)

## Installation

```bash
pip install -e ".[dev]"
```

## Running the app

```bash
log-viewer
```

Or directly via Python:

```bash
python -m logviewer.main
```

## Running tests

```bash
pytest
```

## Linting and formatting

```bash
# Check for lint errors
ruff check .

# Auto-fix lint errors
ruff check --fix .

# Format code
ruff format .
```

## Type checking

```bash
mypy .
```