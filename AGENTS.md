# AGENTS.md - Ótica Price Finder

## Project Overview

Python application to help find the best glasses price in Brazil by sending WhatsApp messages to multiple optical stores. Uses Playwright for WhatsApp Web automation.

## Tech Stack

- **Language**: Python 3.11+
- **Automation**: Playwright (WhatsApp Web) & Evolution API (HTTP Backend)
- **Web Framework**: FastAPI (for optional web UI)
- **Data Storage**: JSON file (simple, no database needed)
- **Containerization**: Docker (for Evolution API)
- **CLI**: Click
- **Testing**: pytest
- **Linting**: ruff
- **Type Checking**: mypy

---

## Build / Lint / Test Commands

### Installation

```bash
# Install project and dependencies
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium
```

### Running the Application

```bash
# CLI - send message to all stores (default: Playwright)
python -m otica_scripts.cli send "Olá, gostaria de saber o preço de um óculos de grau"

# CLI - send message via Evolution API (Recommended for performance)
python -m otica_scripts.cli send "Olá" --provider evolution

# CLI - test with one store using Evolution API
python -m otica_scripts.cli send --test "Teste" --provider evolution

# CLI - add a new store
python -m otica_scripts.cli add-store --name "Ótica Central" --phone "+5511999999999"

# CLI - list all stores
python -m otica_scripts.cli list-stores

# CLI - remove a store
python -m otica_scripts.cli remove-store "Ótica Central"

# Run web UI (optional)
python -m otica_scripts.web_ui
# Then open http://localhost:8000
```

### Running Tests

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_store.py

# Run a single test function
pytest tests/test_store.py::test_add_store

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=otica_scripts --cov-report=term-missing
```

### Linting & Type Checking

```bash
# Run ruff linter
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Run mypy type checker
mypy otica_scripts/

# Run all checks (lint + typecheck)
tox -e lint,typecheck
```

---

## Code Style Guidelines

### General Principles

- **Be explicit** - clarity over cleverness
- **Keep it simple** - minimal dependencies
- **Fail fast with clear messages** - no silent failures

### Imports

```python
# Standard library first, then third-party, then local
import json
from pathlib import Path
from dataclasses import dataclass

import click
from playwright.sync_api import sync_playwright

from otica_scripts.store import Store
from otica_scripts.whatsapp_sender import WhatsAppSender
```

### Formatting

- Line length: 100 characters max
- Use Black for formatting (integrated via ruff)
- 2 empty lines between top-level definitions
- 1 empty line between functions in a class

### Types

```python
# Use type hints everywhere
from dataclasses import dataclass
from typing import Optional

@dataclass
class Store:
    name: str
    phone: str  # Format: +5511999999999
    address: Optional[str] = None

def send_message(phone: str, message: str) -> bool:
    """Send a WhatsApp message to the given phone number."""
    ...
```

### Naming Conventions

- **Variables/functions**: `snake_case` - `store_name`, `send_message`
- **Classes**: `PascalCase` - `Store`, `WhatsAppSender`
- **Constants**: `UPPER_SNAKE_CASE` - `MAX_MESSAGE_LENGTH`
- **Private methods**: `_private_method`
- **Files**: `snake_case.py` - `store.py`, `whatsapp_sender.py`

### Error Handling

```python
# Always use specific exception types
class StoreNotFoundError(Exception):
    """Raised when a store is not found in the database."""
    pass

# Handle errors at the appropriate level
def get_store(name: str) -> Store:
    store = _load_store(name)
    if store is None:
        raise StoreNotFoundError(f"Store '{name}' not found")
    return store
```

### Project Structure

```
otica_scripts/
├── __init__.py           # Package init, version
├── cli.py                # Click CLI commands
├── web_ui.py             # FastAPI web interface (optional)
├── store.py              # Store data model
├── whatsapp_sender.py    # WhatsApp automation
├── config.py             # Configuration
└── data/
    └── stores.json       # Store database

tests/
├── __init__.py
├── test_store.py
├── test_whatsapp_sender.py
└── conftest.py           # Pytest fixtures
```

### Configuration

All configuration via environment variables or a `.env` file:

```bash
# .env example
WHATSAPP_SESSION_FILE=session.json
STORES_DATA_FILE=data/stores.json
LOG_LEVEL=INFO
```

### Key Conventions

1. **Phone numbers**: Always store with country code, no special chars
   - Valid: `+5511999999999`
   - Invalid: `(11) 99999-9999`

2. **Messages**: Warn if message exceeds WhatsApp limit (4096 chars)

3. **Rate limiting**: Add 2-second delay between messages to avoid blocks

4. **Session management**: Save Playwright session to avoid QR code scan every time

5. **Data persistence**: Auto-save store list after every modification using **atomic writes** (write to temp file then replace) to prevent data corruption.

---

## Development Workflow

1. Make changes in a feature branch
2. Run linting: `ruff check --fix .`
3. Run type checking: `mypy otica_scripts/`
4. Run tests: `pytest`
5. Commit with clear message describing the change
