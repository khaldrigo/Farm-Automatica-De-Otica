# AGENTS.md - Buscaí

## LEIA ISSO PRIMEIRO

- Stack: FastAPI (Python 3.12) + PostgreSQL + pgvector + Redis + Next.js 14
- Cidade de referência: Santarém, Pará, Brasil
- TDD é obrigatório: testes antes da implementação, sempre, sem exceção
- Uma tarefa por vez. Não antecipe tarefas futuras.
- Nunca edite migration existente. Sempre crie uma nova.
- Embeddings devem ser regerados quando name, description, tags ou category_ids mudam.


## Project Overview

Buscaí is an open-source local search platform. Users type what they need in natural language,
an AI pipeline interprets the intent, and the system returns direct contact links (WhatsApp,
Instagram, Facebook, phone) to local businesses and service providers.

Designed to be self-hosted per city. The reference instance covers Santarém, Pará, Brazil.

## Repository Structure

```
buscai/
├── frontend/        # Next.js 14 (App Router, TypeScript, Tailwind)
├── backend/         # FastAPI (Python 3.12, SQLAlchemy, Alembic)
├── docker-compose.yml
├── .env.example
└── .github/
    └── workflows/
        └── ci.yml
```

---

## Tech Stack

### Backend
- **Language**: Python 3.12+ with strict mypy
- **Framework**: FastAPI + Uvicorn
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Database**: PostgreSQL 16 + pgvector extension
- **Cache / Queue broker**: Redis
- **Workers**: Celery
- **NLP / Embeddings**: Ollama (default, local) or OpenAI API (configurable)
- **Testing**: pytest + pytest-asyncio + httpx (async test client)
- **Linting**: ruff
- **Type checking**: mypy

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS (core utilities only)
- **Testing**: Vitest + Testing Library
- **E2E**: Playwright

---

## Environment Variables

Copy `.env.example` to `.env` before running anything locally.

```bash
# Database
DATABASE_URL=postgresql+asyncpg://buscai:buscai@localhost:5432/buscai

# Redis
REDIS_URL=redis://localhost:6379/0

# AI provider: "ollama" or "openai"
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=                        # only required if AI_PROVIDER=openai

# City config (per-instance)
CITY_NAME=Santarém
CITY_SLUG=santarem
CITY_STATE=PA

# Auth
SECRET_KEY=change-me-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Storage (Cloudflare R2 or S3-compatible)
STORAGE_BUCKET_URL=
STORAGE_ACCESS_KEY=
STORAGE_SECRET_KEY=

# Logging
LOG_LEVEL=INFO
```

---

## Build / Lint / Test Commands

### Backend

```bash
cd backend

# Install dependencies
pip install -e ".[dev]"

# Start all services (postgres, redis, ollama)
docker compose up -d

# Run migrations
alembic upgrade head

# Seed initial data (categories, etc.)
python -m app.seed

# Start dev server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest                                         # all tests
pytest tests/unit/                             # unit only
pytest tests/integration/                      # integration only
pytest -k "test_search"                        # filter by name
pytest --cov=app --cov-report=term-missing     # with coverage

# Lint + type check
ruff check .
ruff check --fix .
mypy app/
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev        # http://localhost:3000

# Run unit/component tests
npm run test
npm run test:watch

# Run E2E tests (requires backend running)
npm run test:e2e

# Build
npm run build
npm run lint
```

---

## TDD — Non-Negotiable Rule

**Agents must always write tests before writing implementation code.**

The required order for every task is:

1. Write the test(s) that describe the expected behavior
2. Run the tests — they MUST fail at this point
3. Write the minimum implementation to make them pass
4. Refactor if needed, keeping tests green

If an agent writes implementation before tests, the task is considered incomplete.
Do not skip this step even for "trivial" changes.

---

## Database Conventions

### Migrations

- **Never edit an existing migration file.** Always create a new one.
- Migration names must be descriptive: `alembic revision -m "add_embedding_to_establishments"`
- Every schema change requires a corresponding migration before merging.
- Run `alembic upgrade head` before running tests that touch the database.

### Models

- All models inherit from `Base` (SQLAlchemy declarative base)
- Always include `id` (UUID), `created_at`, `updated_at`
- Soft delete: use `status` ENUM field, never hard DELETE on user-facing entities
- `slug` fields must have a UNIQUE constraint and a non-null check

### Embeddings

The `embedding` column (vector(1536)) on `Establishment` must be regenerated
whenever any of these fields change: `name`, `description`, `tags`, `category_ids`.

This is handled by the `EmbeddingService`. Never update these fields without
calling `EmbeddingService.refresh(establishment_id)` afterward (or enqueue a
Celery task `tasks.refresh_embedding`).

---

## API Conventions

### Response Shape

All API responses follow this envelope:

```json
// Success (list)
{
  "data": [...],
  "meta": { "total": 100, "page": 1, "per_page": 20 }
}

// Success (single)
{
  "data": { ... }
}

// Error
{
  "error": {
    "code": "ESTABLISHMENT_NOT_FOUND",
    "message": "No establishment found with slug 'foo'"
  }
}
```

### HTTP Status Codes

- `200` — success
- `201` — created
- `204` — deleted (no body)
- `400` — bad request / validation error
- `401` — unauthenticated
- `403` — forbidden (authenticated but not allowed)
- `404` — not found
- `422` — unprocessable entity (Pydantic validation)
- `429` — rate limited
- `500` — internal server error (never expose stack traces in production)

### Pagination

All list endpoints accept `?page=1&per_page=20`. Default `per_page` is 20, max is 100.

---

## Code Style

### Python

```python
# Imports: stdlib → third-party → local
import uuid
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.establishment import Establishment
from app.services.search import SearchService
```

- Line length: 100 characters
- Ruff handles formatting (replaces Black)
- 2 blank lines between top-level definitions
- Type hints everywhere — mypy must pass with no errors

```python
# Use specific exception classes, never bare Exception
class EstablishmentNotFoundError(Exception):
    """Raised when no establishment matches the given identifier."""

# Fail fast, clear messages
def get_by_slug(slug: str) -> Establishment:
    result = _query_by_slug(slug)
    if result is None:
        raise EstablishmentNotFoundError(f"Establishment '{slug}' not found")
    return result
```

### Naming

| Type | Convention | Example |
|---|---|---|
| Variables / functions | snake_case | `get_establishment` |
| Classes | PascalCase | `EstablishmentService` |
| Constants | UPPER_SNAKE_CASE | `MAX_SEARCH_RESULTS` |
| Private methods | `_prefix` | `_build_query` |
| Files | snake_case | `establishment_service.py` |
| API routes | kebab-case | `/api/search-results` |

### TypeScript (Frontend)

- Strict mode enabled (`"strict": true` in tsconfig)
- No `any` — use `unknown` and narrow explicitly
- Components: PascalCase function components only, no class components
- Hooks: prefix with `use` — `useSearch`, `useEstablishment`
- All API calls go through `lib/api.ts`, never `fetch` directly in components

---

## Phone Number Conventions

- Always store with country code, no special characters
- Valid: `+5593912345678`
- Invalid: `(93) 91234-5678`
- Normalization is handled by `app.utils.phone.normalize_br_phone()`
- This function handles: 9-digit mobile, 8-digit landline, strips 0800, removes special chars
- Always run input through this before saving to the database

---

## Contact Link Generation

WhatsApp links must include a pre-filled message with context:

```python
# backend/app/utils/contact_links.py
def whatsapp_link(phone: str, establishment_name: str, user_query: str) -> str:
    text = f"Olá, vi o perfil de {establishment_name} no Buscaí e preciso de: {user_query}"
    encoded = urllib.parse.quote(text)
    return f"https://wa.me/{phone.replace('+', '')}?text={encoded}"
```

Available platforms: `whatsapp`, `instagram`, `facebook`, `phone`, `website`.
Only generate links for platforms that have a non-null value in the establishment record.

---

## Scraper Conventions

- Always check and respect `robots.txt` before scraping any domain
- Minimum 2-second delay between requests to the same domain
- Use `app.scrapers.base.BaseScraper` — never make raw HTTP calls in scraper code
- Scraped entries are saved with `status = "pending_review"`, never `"active"` directly
- A human operator (or admin panel) must approve before entries go live
- Never collect: CPF, RG, personal home addresses, or any sensitive personal data

---

## Celery Tasks

- All tasks live in `app/workers/tasks/`
- Tasks must be idempotent — safe to retry without side effects
- Always set `max_retries=3` and `default_retry_delay=60`
- Task names follow: `domain.action` — e.g. `embedding.refresh`, `scraper.run_google_maps`

```python
@app.task(bind=True, max_retries=3, default_retry_delay=60)
def refresh_embedding(self, establishment_id: str) -> None:
    try:
        EmbeddingService().refresh(establishment_id)
    except Exception as exc:
        raise self.retry(exc=exc)
```

---

## Testing Conventions

### Backend (pytest)

- Unit tests: `tests/unit/` — no database, no network, mock all I/O
- Integration tests: `tests/integration/` — use a real test database (separate from dev)
- Every new endpoint needs at least: happy path, missing required fields (422), not found (404)
- Every new service method needs at least: expected output, edge case, error case
- Use `pytest.mark.asyncio` for all async tests
- Fixtures live in `tests/conftest.py`

```python
# Example test structure
def test_normalize_celular_com_9():
    assert normalize_br_phone("(93) 9 1234-5678") == "+5593912345678"

def test_normalize_rejects_0800():
    assert normalize_br_phone("0800 123 4567") is None

async def test_create_establishment_missing_name_returns_422(client):
    response = await client.post("/api/establishments", json={"phone": "+5593900000000"})
    assert response.status_code == 422
```

### Frontend (Vitest + Testing Library)

- Test behavior, not implementation — query by role/label, not by class or id
- No snapshot tests unless absolutely necessary
- E2E tests (Playwright) live in `frontend/e2e/` and cover critical user flows only:
  - Search → view results → click contact
  - Profile page loads by slug
  - Review submission

---

## Development Workflow

1. Create a feature branch: `git checkout -b feat/F1-01-establishment-crud`
2. Write tests first (see TDD rule above)
3. Implement until tests pass
4. Run the full check suite before opening a PR:
   ```bash
   # Backend
   ruff check . && mypy app/ && pytest

   # Frontend
   npm run lint && npm run test
   ```
5. PRs require all CI checks to pass — no merging red builds
6. Branch naming: `feat/TASK-ID-short-description`, `fix/description`, `chore/description`
7. Commit messages: imperative mood — "Add establishment CRUD" not "Added" or "Adding"
