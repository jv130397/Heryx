# ADR-003 — JSON nativo versionado e SQLite como armazenamento de trabalho

- **Estado:** proposto; confirmar na Fase 4 após protótipo de migração
- **Decisão proposta:** SQLite é o armazenamento local transacional; JSON nativo documentado é o formato de intercâmbio/backup do próprio aplicativo. Phenopackets e GA4GH são adaptadores, não o modelo interno.
- **Motivo:** nenhum padrão externo auditado cobre simultaneamente fatos clínicos, relações complexas, proveniência, layout e estados de ausência.
- **Risco:** duas representações exigem testes de round-trip e migrações explícitas.

