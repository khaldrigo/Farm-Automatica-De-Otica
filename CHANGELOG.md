# Changelog - Integração Evolution API

Todas as mudanças notáveis para este projeto durante a implementação da Evolution API.

## [1.1.0] - 12/03/2026

### Adicionado
- **Integração com Evolution API**: Adicionado suporte para envio de mensagens via API HTTP usando o backend da Evolution API.
- **Novo Sistema de Provedores**: O CLI agora suporta `--provider evolution` e `--provider playwright` (padrão).
- **Suporte Docker**: Adicionado `docker-compose.yml` e instruções otimizadas de `docker run` para Evolution API v1.8.2.
- **Pareamento Automático**: Suporte para escanear QR Codes diretamente pelo terminal no provedor de API.
- **Variáveis de Ambiente**: Novas opções de configuração no `.env.example` para URL da API, Chave e Nome da Instância.
- **Testes**: Adicionados testes para a implementação do `EvolutionSender`.

### Corrigido
- **Permissões Docker**: Resolvido problemas de permissão com o socket do Docker no Linux.
- **Tipagem (Type Hinting)**: Melhorada a tipagem em `whatsapp_sender.py` para o contexto do navegador Playwright.
- **Compatibilidade**: Alcançado estado estável usando Evolution API v1.8.2 para evitar erros de manifesto OCI em ambientes Docker mais antigos.

### Atualizado
- **CLI**: Comando `send` otimizado com modo de teste e seleção de provedor.
- **Documentação**: Atualizações abrangentes no `README.md` e `AGENTS.md` cobrindo o novo backend profissional.
- **Git**: Adicionados volumes de dados do Docker e arquivos de sessão ao `.gitignore`.
