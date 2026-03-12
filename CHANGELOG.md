# Changelog - Evolution API Integration

All notable changes to this project during the Evolution API implementation.

## [1.1.0] - 2026-03-12

### Added
- **Evolution API Integration**: Added support for sending WhatsApp messages via HTTP API using the Evolution API backend.
- **New Provider System**: CLI now supports `--provider evolution` and `--provider playwright` (default).
- **Docker Support**: Added `docker-compose.yml` and optimized `docker run` instructions for Evolution API v1.8.2.
- **Auto-Pairing**: Support for scanning QR codes directly from the terminal for the API provider.
- **Environment Variables**: New configuration options in `.env.example` for API URL, Key, and Instance name.
- **Tests**: Added tests for the `EvolutionSender` implementation.

### Fixed
- **Docker Permissions**: Resolved permission issues with the Docker socket on Linux.
- **Type Hinting**: Improved type hinting in `whatsapp_sender.py` for Playwright browser context.
- **Compatibility**: Reached a stable state using Evolution API v1.8.2 to avoid OCI manifest errors in older Docker environments.

### Updated
- **CLI**: Optimized `send` command with test mode and provider selection.
- **Documentation**: Comprehensive updates to `README.md` and `AGENTS.md` covering the new professional backend.
- **Git**: Added Docker data volumes and session files to `.gitignore`.
