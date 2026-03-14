#!/usr/bin/env bash

set -euo pipefail

OWNER="khaldrigo"
REPO="Farm-Automatica-De-Otica"
PROJECT_NUMBER="1"

create_label_if_missing() {
  local name="$1"
  local color="$2"

  if ! gh label list --repo "$OWNER/$REPO" --limit 200 | awk '{print $1}' | grep -qx "$name"; then
    gh label create "$name" --color "$color" --repo "$OWNER/$REPO"
    echo "Label criada: $name"
  else
    echo "Label já existe: $name"
  fi
}

create_issue_and_add_to_project() {
  local title="$1"
  local body="$2"
  local labels="$3"

  echo "Criando issue: $title"

  ISSUE_URL=$(gh issue create \
    --repo "$OWNER/$REPO" \
    --title "$title" \
    --body "$body" \
    --label "$labels")

  echo "Issue criada: $ISSUE_URL"

  gh project item-add "$PROJECT_NUMBER" \
    --owner "$OWNER" \
    --url "$ISSUE_URL"

  echo "Adicionada ao project: $title"
  echo "----------------------------------------"
}

# labels da fase 1
create_label_if_missing "fase-1" "FF6B00"
create_label_if_missing "backend" "1d76db"

create_issue_and_add_to_project \
"F1-01: CRUD de Establishment via API" \
"## Objetivo
Implementar CRUD de Establishment via API.

## Testes (TDD)
- test_create_establishment_valid()
- test_create_without_required_fields_returns_422()
- test_get_by_slug()
- test_update_preserves_unchanged_fields()
- test_soft_delete()

## Dependências
- F0-02

## Prioridade
CRÍTICO" \
"fase-1,backend"

create_issue_and_add_to_project \
"F1-02: CRUD de Categories (hierárquica)" \
"## Objetivo
Implementar CRUD de categorias hierárquicas.

## Testes (TDD)
- test_create_root_category()
- test_create_child_category()
- test_get_tree_returns_nested_structure()
- test_category_with_children_not_deletable()

## Dependências
- F0-02

## Prioridade
CRÍTICO" \
"fase-1,backend"

create_issue_and_add_to_project \
"F1-03: Normalização e validação de telefones BR" \
"## Objetivo
Implementar normalização e validação de telefones brasileiros.

## Testes (TDD)
- test_normalize_celular_com_9()
- test_normalize_fixo()
- test_rejects_0800()
- test_rejects_invalid_format()

## Dependências
- F1-01

## Prioridade
ALTO" \
"fase-1,backend"

create_issue_and_add_to_project \
"F1-04: Geração de slug único automático" \
"## Objetivo
Gerar slug único automaticamente para establishments.

## Testes (TDD)
- test_slug_from_name()
- test_slug_collision_adds_suffix()
- test_slug_sanitizes_special_chars()

## Dependências
- F1-01

## Prioridade
ALTO" \
"fase-1,backend"

create_issue_and_add_to_project \
"F1-05: CRUD de Reviews" \
"## Objetivo
Implementar CRUD de reviews.

## Testes (TDD)
- test_create_review_valid()
- test_rating_updates_establishment_avg()
- test_anonymous_review_allowed()
- test_duplicate_review_from_same_user_rejected()

## Dependências
- F1-01

## Prioridade
ALTO" \
"fase-1,backend"

create_issue_and_add_to_project \
"F1-06: Geração de embedding automático ao salvar estabelecimento" \
"## Objetivo
Gerar embedding automaticamente ao criar/atualizar establishment.

## Testes (TDD)
- test_embedding_generated_on_create()
- test_embedding_regenerated_on_update()
- test_embedding_dimension_is_1536()

## Dependências
- F1-01

## Prioridade
MÉDIO" \
"fase-1,backend"

create_issue_and_add_to_project \
"F1-07: Endpoints de listagem com paginação e filtros" \
"## Objetivo
Implementar listagem com paginação e filtros.

## Testes (TDD)
- test_pagination_returns_correct_page()
- test_filter_by_category()
- test_filter_by_verified()
- test_filter_by_price_range()

## Dependências
- F1-01

## Prioridade
ALTO" \
"fase-1,backend"

echo "Fase 1 criada com sucesso."
