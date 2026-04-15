# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install (includes dev dependencies)
pip install -e ".[dev]"

# Run
log-viewer
python -m logviewer.main

# Tests
pytest
pytest tests/test_foo.py::TestClass::test_name   # single test

# Lint
ruff check .          # check
ruff check --fix .    # auto-fix
ruff format .         # format

# Type check
mypy .
```

Line length is 100 characters (configured in `pyproject.toml`).

## Docstring style

Use Sphinx/reStructuredText style throughout — `:param name:`, `:returns:`, `:raises ExceptionType:`, `:ivar name:`. This matches PyCharm's default docstring format.

## Architecture

The app is a GTK 3 log viewer for the systemd journal, structured in clean layers with dependency injection at the top.

**`logviewer/models/`** — Plain data transfer objects. `LogQuery` carries a start datetime, end datetime, and optional regex filter pattern from the UI to the reader.

**`logviewer/readers/`** — `LogReader` (ABC) defines the interface the UI depends on. `JournalctlLogReader` is the only concrete implementation; it translates a `LogQuery` into a `journalctl` subprocess invocation. The reader is injected into the window at construction time, keeping the UI layer decoupled from the log source.

**`logviewer/ui/gtk/`** — GTK widgets. `LogViewer` (the main window) composes a `Toolbar` and a scrollable `TextView`. The `Toolbar` emits a custom `query-ready` GTK signal carrying the constructed `LogQuery`; the window handles it by calling `reader.read_logs()` and populating the text view.

**`logviewer/system/`** — Startup requirement checks (Linux, systemd, journalctl). Failures surface as a GTK error dialog via `main.py` rather than crashing to stderr.

**`logviewer/utils/`** — Locale-aware date format detection (`locale_utils`) and date formatting helpers.

**`logviewer/main.py`** — Entry point. Runs requirement checks, constructs `JournalctlLogReader`, detects the system date format once (locale setting is a process-wide side effect), then creates and shows `LogViewer`.

### GTK import ordering

`gi.require_version('Gtk', '3.0')` must be called before any `gi.repository` imports — this is a PyGObject requirement. `ruff` E402 is suppressed for `main.py` and all `ui/gtk/` files for this reason.
