# ADR-002 — Domínio independente e arquitetura em camadas

- **Estado:** aceito em 2026-10-30
- **Decisão:** `domain` não depende de Qt, SQLite ou adaptadores. UI e importadores chamam casos de uso; persistência implementa portas do aplicativo; rendering recebe projeção imutável de fatos + layout.
- **Motivo:** decisões de layout não podem alterar relações ou dados genéticos, e regras científicas precisam ser testáveis sem GUI.
- **Verificação:** `tests/unit/test_architecture.py` rejeita dependências proibidas no domínio.

