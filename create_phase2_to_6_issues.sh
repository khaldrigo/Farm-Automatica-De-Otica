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

  ADD_OUTPUT=$(gh project item-add "$PROJECT_NUMBER" \
    --owner "$OWNER" \
    --url "$ISSUE_URL" 2>&1) || true

  if echo "$ADD_OUTPUT" | grep -q "Content already exists in this project"; then
    echo "Issue já estava no project, seguindo..."
  else
    echo "$ADD_OUTPUT"
  fi

  echo "Processada: $title"
  echo "----------------------------------------"
}

# labels
create_label_if_missing "fase-2" "FFAA00"
create_label_if_missing "fase-3" "FFD000"
create_label_if_missing "fase-4" "00BFFF"
create_label_if_missing "fase-5" "8A2BE2"
create_label_if_missing "fase-6" "00FF7F"
create_label_if_missing "backend" "1d76db"
create_label_if_missing "frontend" "a371f7"
create_label_if_missing "infra" "0e8a16"

# =========================
# FASE 2 — Motor de Busca
# =========================

create_issue_and_add_to_project \
"F2-01: NLP Pipeline: interpretação de intenção da query" \
"## Objetivo
Implementar pipeline NLP para interpretar a intenção da query.

## Testes (TDD)
- test_query_encanador_returns_category_hidraulica()
- test_query_com_bairro_extrai_localizacao()
- test_query_vaga_retorna_categorias_sugeridas()

## Dependências
- F1-06

## Prioridade
CRÍTICO" \
"fase-2,backend"

create_issue_and_add_to_project \
"F2-02: Full-text search em português (tsvector)" \
"## Objetivo
Implementar busca full-text em português usando tsvector.

## Testes (TDD)
- test_search_finds_by_name()
- test_search_finds_by_tag()
- test_search_handles_accents()
- test_search_handles_synonyms()

## Dependências
- F1-01

## Prioridade
CRÍTICO" \
"fase-2,backend"

create_issue_and_add_to_project \
"F2-03: Busca vetorial semântica (pgvector)" \
"## Objetivo
Implementar busca vetorial semântica com pgvector.

## Testes (TDD)
- test_semantic_search_returns_relevant_results()
- test_similar_query_same_results()
- test_results_ordered_by_cosine_similarity()

## Dependências
- F1-06

## Prioridade
ALTO" \
"fase-2,backend"

create_issue_and_add_to_project \
"F2-04: Busca híbrida com scoring unificado" \
"## Objetivo
Unificar full-text e busca semântica com fórmula de scoring.

## Testes (TDD)
- test_hybrid_score_formula()
- test_high_rated_above_low_rated_same_relevance()
- test_complete_profile_above_incomplete()

## Dependências
- F2-02
- F2-03

## Prioridade
CRÍTICO" \
"fase-2,backend"

create_issue_and_add_to_project \
"F2-05: Cache de resultados de busca (Redis)" \
"## Objetivo
Implementar cache de busca com Redis.

## Testes (TDD)
- test_same_query_returns_cached()
- test_cache_invalidated_on_establishment_update()
- test_cache_ttl_respected()

## Dependências
- F2-04

## Prioridade
MÉDIO" \
"fase-2,backend"

create_issue_and_add_to_project \
"F2-06: Endpoint /api/search principal" \
"## Objetivo
Implementar endpoint principal de busca.

## Testes (TDD)
- test_search_returns_correct_shape()
- test_empty_query_returns_featured()
- test_no_results_returns_empty_not_500()

## Dependências
- F2-04

## Prioridade
CRÍTICO" \
"fase-2,backend"

# =========================
# FASE 3 — Frontend Web
# =========================

create_issue_and_add_to_project \
"F3-01: Página inicial: campo de busca hero" \
"## Objetivo
Implementar homepage com campo de busca principal.

## Testes (TDD)
- test_search_input_renders()
- test_submit_navigates_to_results()
- test_placeholder_suggestions_visible()

## Dependências
- F2-06

## Prioridade
CRÍTICO" \
"fase-3,frontend"

create_issue_and_add_to_project \
"F3-02: Página de resultados: grid de cards" \
"## Objetivo
Implementar página de resultados com grid de cards.

## Testes (TDD)
- test_cards_render_with_data()
- test_no_results_shows_empty_state()
- test_loading_skeleton_shows_during_fetch()

## Dependências
- F3-01

## Prioridade
CRÍTICO" \
"fase-3,frontend"

create_issue_and_add_to_project \
"F3-03: Card de estabelecimento: botões de contato direto" \
"## Objetivo
Implementar botões de contato direto no card.

## Testes (TDD)
- test_whatsapp_link_correct_format()
- test_instagram_link_opens_correct_url()
- test_hidden_if_no_contact_available()

## Dependências
- F3-02

## Prioridade
CRÍTICO" \
"fase-3,frontend"

create_issue_and_add_to_project \
"F3-04: Página de perfil do estabelecimento (/p/[slug])" \
"## Objetivo
Implementar página pública de perfil do estabelecimento.

## Testes (TDD)
- test_profile_loads_by_slug()
- test_all_fields_rendered()
- test_404_for_invalid_slug()

## Dependências
- F3-02

## Prioridade
ALTO" \
"fase-3,frontend"

create_issue_and_add_to_project \
"F3-05: Componente de avaliação: listar e criar" \
"## Objetivo
Implementar listagem e criação de avaliações no frontend.

## Testes (TDD)
- test_reviews_listed_with_stars()
- test_submit_review_sends_post()
- test_rating_distribution_chart_renders()

## Dependências
- F3-04
- F1-05

## Prioridade
ALTO" \
"fase-3,frontend"

create_issue_and_add_to_project \
"F3-06: Filtros de busca: categoria, bairro, avaliação, preço" \
"## Objetivo
Implementar filtros na tela de busca.

## Testes (TDD)
- test_filter_updates_url_params()
- test_filter_triggers_new_search()
- test_active_filter_visually_highlighted()

## Dependências
- F3-02

## Prioridade
ALTO" \
"fase-3,frontend"

create_issue_and_add_to_project \
"F3-07: SEO: meta tags dinâmicas, sitemap, robots.txt" \
"## Objetivo
Implementar SEO técnico para buscas locais.

## Testes (TDD)
- test_search_page_has_meta_title()
- test_profile_has_structured_data_json_ld()
- test_sitemap_lists_all_active_establishments()

## Dependências
- F3-04

## Prioridade
MÉDIO" \
"fase-3,frontend"

# =========================
# FASE 4 — Scraper / Coleta
# =========================

create_issue_and_add_to_project \
"F4-01: Scraper base: Google Maps (dados públicos de negócios)" \
"## Objetivo
Implementar scraper base para dados públicos de negócios.

## Testes (TDD)
- test_scraper_extracts_name_phone_address()
- test_phone_normalized_after_scrape()
- test_duplicate_detection_by_phone_or_name()

## Dependências
- F1-01

## Prioridade
ALTO" \
"fase-4,backend"

create_issue_and_add_to_project \
"F4-02: Scraper: Instagram Business profiles públicos" \
"## Objetivo
Implementar coleta de perfis públicos de Instagram Business.

## Testes (TDD)
- test_extracts_handle_and_bio()
- test_extracts_contact_if_public()
- test_handles_private_profile_gracefully()

## Dependências
- F4-01

## Prioridade
MÉDIO" \
"fase-4,backend"

create_issue_and_add_to_project \
"F4-03: Celery task: scraping assíncrono com retry" \
"## Objetivo
Executar scraping assíncrono com retry e limites.

## Testes (TDD)
- test_task_retries_on_network_error()
- test_task_marks_failed_after_max_retries()
- test_rate_limit_respected_between_requests()

## Dependências
- F0-01
- F4-01

## Prioridade
ALTO" \
"fase-4,backend,infra"

create_issue_and_add_to_project \
"F4-04: Deduplicação: detectar e mesclar duplicatas" \
"## Objetivo
Detectar duplicatas e permitir merge de dados.

## Testes (TDD)
- test_same_phone_detected_as_duplicate()
- test_fuzzy_name_match_suggests_merge()
- test_merge_preserves_all_data()

## Dependências
- F1-01

## Prioridade
MÉDIO" \
"fase-4,backend"

create_issue_and_add_to_project \
"F4-05: Painel admin: revisar/aprovar entradas do scraper" \
"## Objetivo
Criar painel admin para revisão das entradas coletadas.

## Testes (TDD)
- test_pending_entries_listed()
- test_approve_marks_as_active()
- test_reject_with_reason()

## Dependências
- F4-01

## Prioridade
ALTO" \
"fase-4,frontend,backend"

create_issue_and_add_to_project \
"F4-06: Formulário de autocadastro público" \
"## Objetivo
Criar formulário público para autocadastro de negócios.

## Testes (TDD)
- test_form_submission_creates_pending_establishment()
- test_spam_prevention_rate_limit()
- test_owner_receives_confirmation_via_whatsapp()

## Dependências
- F1-01

## Prioridade
ALTO" \
"fase-4,frontend,backend"

# =========================
# FASE 5 — Auth e Gestão de Perfil
# =========================

create_issue_and_add_to_project \
"F5-01: Auth de operadores (JWT): login/logout" \
"## Objetivo
Implementar autenticação de operadores com JWT.

## Testes (TDD)
- test_login_valid_credentials_returns_token()
- test_invalid_credentials_returns_401()
- test_expired_token_rejected()

## Dependências
- F0-02

## Prioridade
ALTO" \
"fase-5,backend"

create_issue_and_add_to_project \
"F5-02: Claim de estabelecimento pelo dono" \
"## Objetivo
Permitir claim de estabelecimento pelo dono com link de verificação.

## Testes (TDD)
- test_claim_sends_verification_link()
- test_verification_link_expires_in_24h()
- test_claimed_establishment_editable_by_owner()

## Dependências
- F5-01

## Prioridade
MÉDIO" \
"fase-5,backend"

create_issue_and_add_to_project \
"F5-03: Painel do dono: editar perfil, fotos, horários" \
"## Objetivo
Criar painel do dono para editar dados do estabelecimento.

## Testes (TDD)
- test_owner_can_update_own_establishment()
- test_owner_cannot_update_others()
- test_photo_upload_validates_mime_type()

## Dependências
- F5-02

## Prioridade
MÉDIO" \
"fase-5,frontend,backend"

create_issue_and_add_to_project \
"F5-04: Resposta do dono a avaliações" \
"## Objetivo
Permitir resposta do dono às avaliações.

## Testes (TDD)
- test_owner_can_reply_to_review()
- test_owner_cannot_reply_twice()
- test_reply_visible_on_profile()

## Dependências
- F5-03
- F1-05

## Prioridade
BAIXO" \
"fase-5,frontend,backend"

# =========================
# FASE 6 — Qualidade / Performance / Deploy
# =========================

create_issue_and_add_to_project \
"F6-01: Testes E2E com Playwright: fluxo de busca completo" \
"## Objetivo
Cobrir fluxo principal de busca com testes E2E.

## Testes (TDD)
- test_e2e_search_to_contact_click()
- test_e2e_profile_page_loads()
- test_e2e_review_submission()

## Dependências
- F3-03
- F3-05

## Prioridade
ALTO" \
"fase-6,frontend,backend"

create_issue_and_add_to_project \
"F6-02: Performance: índices de banco otimizados" \
"## Objetivo
Otimizar índices de banco para performance de busca.

## Testes (TDD)
- test_search_query_under_200ms_with_1000_records()
- test_explain_analyze_uses_indexes()

## Dependências
- F2-06

## Prioridade
ALTO" \
"fase-6,backend"

create_issue_and_add_to_project \
"F6-03: Rate limiting na API pública" \
"## Objetivo
Aplicar rate limiting na API pública.

## Testes (TDD)
- test_100_requests_per_minute_allowed()
- test_101st_request_returns_429()
- test_rate_limit_per_ip()

## Dependências
- F0-01

## Prioridade
ALTO" \
"fase-6,backend,infra"

create_issue_and_add_to_project \
"F6-04: Documentação: README, CONTRIBUTING, deploy guide" \
"## Objetivo
Documentar setup, contribuição e deploy do projeto.

## Testes (TDD)
- test_docker_compose_up_starts_from_fresh_clone()
- test_seed_script_runs_without_errors()

## Dependências
- Todas as fases

## Prioridade
ALTO" \
"fase-6,infra"

create_issue_and_add_to_project \
"F6-05: Deploy na Vercel (frontend) + Railway/Fly.io (backend)" \
"## Objetivo
Preparar deploy de produção do frontend e backend.

## Testes (TDD)
- test_production_build_succeeds()
- test_env_vars_validated_on_startup()
- test_healthcheck_200_in_production()

## Dependências
- F6-04

## Prioridade
ALTO" \
"fase-6,infra,frontend,backend"

echo "Fases 2 a 6 criadas com sucesso."
