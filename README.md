# Ótica Price Finder

Aplicativo para enviar mensagens via WhatsApp para múltiplas ópticas no Brasil, útil para comparar preços de óculos, lentes e exames.

## Instalação

### 1. Clone o repositório
```bash
git clone <repo-url>
cd otica_scripts
```

### 2. Crie um ambiente virtual
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -e ".[dev]"
playwright install chromium
```

### 4. Configure o ambiente
```bash
cpenv
```

## .env.example . Uso

### Interface Web (Recomendado)

1. Inicie o servidor:
```bash
python -m otica_scripts.web_ui
```

2. Abra no navegador: http://localhost:8000

3. Use a interface para:
   - **Importar Lojas**: Adicione várias ópticas de uma vez (nome, telefone, Instagram)
   - **Gerar Links WhatsApp**: Crie links para enviar mensagens manualmente
   - **Acompanhar Respostas**: Marque quando uma loja responder

### Linha de Comando

#### Adicionar uma loja
```bash
python -m otica_scripts.cli add-store --name "Ótica Central" --phone "+5593991111111"
```

#### Listar lojas
```bash
python -m otica_scripts.cli list-stores
```

#### Importar lojas do CSV
```bash
python -m otica_scripts.cli import-csv lojas.csv
```

Formato CSV:
```csv
name,phone,instagram
Ótica Central,5593991111111,@oticacentral
Ótica Brasil,5593992222222
```

#### Enviar mensagem para todas as lojas
```bash
python -m otica_scripts.cli send "Olá! Gostaria de saber o preço de um óculos de grau."
```

#### Testar com 1 loja apenas
```bash
python -m otica_scripts.cli send --test "Mensagem de teste"
```

#### Ver sem enviar (dry-run)
```bash
python -m otica_scripts.cli send "mensagem" --dry-run
```

## Estrutura do Projeto

```
otica_scripts/
├── otica_scripts/
│   ├── __init__.py       # Versão do pacote
│   ├── cli.py            # Interface de linha de comando
│   ├── config.py         # Configurações
│   ├── store.py         # Modelo de dados das lojas
│   ├── message_tracker.py # Histórico de mensagens
│   ├── whatsapp_sender.py # Automação do WhatsApp
│   ├── scraper.py       # Scraper (opcional)
│   └── web_ui.py        # Interface web
├── templates/
│   └── index.html       # Frontend
├── data/
│   ├── stores.json      # Lojas cadastradas
│   └── messages.json    # Histórico de mensagens
└── tests/               # Testes
```

## Configuração

Variáveis de ambiente (`.env`):
```bash
STORES_DATA_FILE=data/stores.json
MESSAGES_DATA_FILE=data/messages.json
WHATSAPP_SESSION_FILE=session.json
LOG_LEVEL=INFO
```

## Desenvolvimento

### Executar testes
```bash
pytest
```

### Verificar tipos
```bash
mypy otica_scripts/
```

### Verificar estilo
```bash
ruff check .
```

## Notas

- O WhatsApp Web requer login. Na primeira vez, escaneie o QR code.
- A sessão é salva para não precisar escanear novamente.
- Recomenda-se usar a interface web para gerar links do WhatsApp e enviar manualmente.
- O envio automatizado pode ser bloqueado se muitas mensagens forem enviadas rapidamente (aguarde 2 segundos entre mensagens).
