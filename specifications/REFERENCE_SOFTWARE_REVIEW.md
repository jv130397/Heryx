# Revisão de software de referência — Fase 4.5

Consulta em 2026-10-30.

## Open Pedigree

- Fonte: https://github.com/phenotips/open-pedigree
- Licença declarada: LGPL-2.1; copyright Gene42/PhenoTips.
- Stack: aplicação web JavaScript baseada em Prototype e Raphaël.
- Comportamentos observados: suporte a famílias complexas, ligações intergeracionais, consanguinidade, templates, auto-layout e importação de formatos familiares.
- A documentação PhenoTips descreve ações contextuais/handles para pais, irmãos, parceiros, descendentes e relações, além de auto-layout e renumeração de gerações.

## Open Pedigree XML / demonstração de Fabiano Poswar

- Fonte observada: https://fabianoposwar.com/heredograma/
- A página se apresenta como editor web adaptado do Open Pedigree.
- Foi usada somente para observar o fluxo geral de edição. Licença própria e autorização para reutilização de ativos não foram localizadas na página consultada.

## Decisão

Nenhum código, ícone, CSS ou ativo visual foi copiado. Foram adaptados apenas padrões funcionais genéricos: inclusão contextual de familiares, relações explícitas, organização automática, edição contextual e exportação. A identidade visual e toda a implementação são próprias, nativas em Python/PySide6.

