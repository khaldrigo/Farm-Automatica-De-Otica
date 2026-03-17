import os

import pytest
from sqlalchemy import create_engine, inspect


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://buscai:buscai@localhost:5432/buscai"
)


@pytest.fixture(scope="function")
def engine():
    engine = create_engine(DATABASE_URL, echo=False)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def inspector(engine):
    return inspect(engine)


def test_all_tables_created(inspector):
    tables = inspector.get_table_names()

    assert "establishments" in tables, "Tabela establishments não existe"
    assert "categories" in tables, "Tabela categories não existe"
    assert "reviews" in tables, "Tabela reviews não existe"


def test_indexes_exist(inspector):
    indexes = inspector.get_indexes("establishments")
    index_names = [idx["name"] for idx in indexes]

    assert any("slug" in name.lower() for name in index_names), "Índice em slug não existe"

    columns = [col["name"] for col in inspector.get_columns("establishments")]
    if "category_ids" in columns:
        assert any("category_ids" in name.lower() for name in index_names), "Índice em category_ids não existe"


def test_foreign_keys_valid(inspector):
    fks = inspector.get_foreign_keys("reviews")
    has_establishment_fk = any(
        "establishment_id" in fk.get("constrained_columns", [])
        for fk in fks
    )
    assert has_establishment_fk, "FK para establishment em reviews não existe"

    fks_categories = inspector.get_foreign_keys("categories")
    parent_fk_exists = any(
        "parent_id" in fk.get("constrained_columns", [])
        for fk in fks_categories
    )
    assert parent_fk_exists, "FK self-referência para parent_id em categories não existe"


def test_establishment_columns(inspector):
    columns = {col["name"]: col for col in inspector.get_columns("establishments")}

    assert "id" in columns
    assert "name" in columns
    assert "slug" in columns
    assert "description" in columns
    assert "phone" in columns
    assert "whatsapp" in columns
    assert "instagram" in columns
    assert "facebook" in columns
    assert "website" in columns
    assert "address" in columns
    assert "embedding" in columns
    assert "business_hours" in columns
    assert "attributes" in columns
    assert "status" in columns


def test_category_columns(inspector):
    columns = {col["name"]: col for col in inspector.get_columns("categories")}

    assert "id" in columns
    assert "name" in columns
    assert "slug" in columns
    assert "parent_id" in columns
    assert "search_synonyms" in columns


def test_review_columns(inspector):
    columns = {col["name"]: col for col in inspector.get_columns("reviews")}

    assert "id" in columns
    assert "establishment_id" in columns
    assert "user_id" in columns
    assert "rating" in columns
    assert "comment" in columns
