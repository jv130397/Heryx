# Arquitetura da Fase 3

O esqueleto e as fronteiras de módulos foram materializados na Fase 3. A interface, persistência e motor gráfico permanecem deliberadamente sem implementação até a Fase 4.

## Stack

- Python 3.12 em Conda; PySide6/Qt 6 e `QGraphicsScene/QGraphicsView` planejados para o canvas vetorial.
- Pydantic v2 para modelos de fronteira/validação; domínio interno não deve depender da GUI.
- SQLite via camada repository e migrações explícitas; avaliar SQLAlchemy/Alembic somente após medir custo/empacotamento.
- SVG como formato gráfico canônico de exportação; Qt para PNG/PDF.
- pytest, pytest-qt, testes property-based seletivos e golden SVG normalizado.
- Empacotamento a decidir após diagnóstico: wheel/venv primeiro; AppImage ou pacote Debian somente após testes no Ubuntu-alvo.

## Módulos

```text
src/rarepedigree/
  domain/          # entidades e invariantes, sem Qt/SQLite
  application/     # casos de uso, comandos, undo/redo
  rules/           # validação PED-* e diagnósticos
  rendering/       # símbolos, layout, legenda, SVG
  ui/              # PySide6, controllers/view-models
  persistence/     # SQLite, migrações, backups
  terminology/     # HPO/ORPHA/MONDO cache versionado
  genetics/        # HGVS, genótipo, segregação explicável
  interchange/     # JSON, PED/FAM, Phenopackets, GA4GH experimental
  privacy/         # pseudonimização e exportação minimizada
```

Fluxo: UI → comandos/casos de uso → domínio → repositórios. Rendering lê uma projeção do domínio + `Layout`; nunca modifica fatos. Importadores produzem DTO + relatório e só então um comando validado persiste.

## Plano do primeiro protótipo (após aprovação)

1. Diagnosticar SO/Python/Qt, registrar ADRs e congelar dependências mínimas.
2. Implementar domínio mínimo (`Project`, `Individual`, `Relationship`, `PhenotypicObservation`, `Layout`) e JSON nativo versionado.
3. Criar testes para PED-001, 004–006 e 009–010 antes do renderizador.
4. Janela PySide6 com canvas, paleta, propriedades e comandos adicionar/mover/relacionar/desfazer.
5. Renderizar somente símbolos confirmados e legenda automática; marcar recursos não normativos como anotação.
6. Salvar/reabrir SQLite, exportar SVG/PNG/PDF e executar round-trip/golden tests.
7. Validar visualmente com as figuras NSGC corrigidas e revisão humana antes de ampliar recursos.

## Riscos/ADRs pendentes

- Licença e atualização offline de HPO/Orphanet; estratégia de cache.
- Maturidade do GA4GH Pedigree e perdas entre modelos.
- Algoritmo de layout para uniões múltiplas, adoção e ART.
- Criptografia local, key management e modelo de ameaças.
- Definição institucional de retenção, consentimento e base legal LGPD.
