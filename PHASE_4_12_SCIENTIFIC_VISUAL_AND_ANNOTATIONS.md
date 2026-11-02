# RarePedigree Studio — Fase 4.12

## Resultado

A Fase 4.12 foi implementada sobre a arquitetura da Fase 4.11, sem recriar o editor e sem
reintroduzir comandos familiares redundantes. A representação usa geometria para
sexo/gênero, estado fenotípico para preenchimento e um contorno neutro único. Anotações de
canvas são objetos de apresentação persistentes, mas permanecem separadas dos fatos
clínicos e do grafo familiar.

Checkpoint anterior às alterações: `cdd7346`.

## Auditoria inicial

- O contorno por sexo/gênero ainda existia nas preferências e na pintura dos símbolos.
- A visualização de preferências misturava forma geométrica e cor de categoria.
- Não existia entidade persistente de anotação, edição no canvas ou política de exportação.
- A Fase 4.11 já havia removido o minimapa, consolidado o zoom e centralizado a criação de
  familiares no indivíduo; essas decisões foram preservadas.
- O diretório `Modelos/` foi apenas consultado e permaneceu sem alterações.

## Matriz de requisitos e aceitação

| Requisito | Implementação | Teste/evidência | Estado |
|---|---|---|---|
| Contorno neutro | `PedigreeRenderStyle.outline_color`; pintura não consulta categoria | `test_geometry_not_color_encodes_gender`; capturas 01/02 | Aceito |
| Geometria científica | quadrado, círculo e losango permanecem como codificação geométrica | suíte histórica e capturas | Aceito |
| Fenótipo configurável | cores de afetado, não afetado, desconhecido, contorno e espessura | `test_phase_4_12_palette_updates_live_preview` | Aceito |
| Paletas | científica, clínica, alto contraste e opção legada acessível | diálogo de preferências real | Aceito |
| Monocromia | preenchimento preto/branco sem apagar `?` e demais marcas | `test_monochrome_preserves_unknown_marker_semantics` | Aceito |
| Compatibilidade | campos de cor antigos mantidos como API, mas sem efeito científico | 140 testes antigos preservados; teste de preferência legada | Aceito |
| Criar anotação | menu do canvas vazio e `Ctrl+Shift+N` | teste de criação/atalho | Aceito |
| Editar/mover/redimensionar | editor, arraste e alça inferior direita | captura 04 e testes de geometria | Aceito |
| Duplicar/excluir | menu contextual; exclusão confirmada | implementação e undo/redo atômico | Aceito |
| Tipos de anotação | geral, revisão, a confirmar e técnica | modelo e editor | Aceito |
| Associação opcional | `individual_id` validado sem alterar indivíduo/relação | round-trip de persistência | Aceito no modelo |
| Persistência | schema `0.3.0`, migração automática e JSON nativo | teste de round-trip e migração | Aceito |
| Não interferir no layout | notas não entram no motor de parentesco/layout | separação de coleção e cena | Aceito |
| Exportação | notas excluídas por padrão; opção explícita em SVG/PNG/PDF | `test_annotation_export_is_opt_in`; captura 05 | Aceito |
| Exportação limpa | seleção, alças e sombra são desativadas durante renderização | exportador compartilhado | Aceito |
| Movimento reduzido | fade curto de entrada, desativável por preferência | configuração `ui/reduce_motion` | Aceito |
| PT-BR/EN | novas ações, diálogos e mensagens no catálogo | captura 06 e catálogo | Aceito |
| Controles de opção acessíveis | fundo branco/borda no estado livre, azul e `✓` redundante no estado marcado | captura 07 e teste de tema | Aceito |
| Fase 4.11 preservada | drawer legado oculto, minimapa ausente, zoom único | validação estrutural | Aceito |

## Arquivos modificados

- `src/rarepedigree/domain/models.py` e `domain/__init__.py`
- `src/rarepedigree/persistence/migrations.py`
- `src/rarepedigree/rendering/style.py`, `items.py`, `scene.py`, `exporters.py` e
  `rendering/__init__.py`
- `src/rarepedigree/ui/main_window.py`, `dialogs.py`, `preferences.py` e `i18n.py`
- `tests/unit/test_migrations.py` e `tests/unit/test_phase_4_12.py`
- `scripts/validate_phase_4_12.py`

## Modelo e comportamento das anotações

`CanvasAnnotation` contém UUID, título, texto, tipo, posição, dimensões, cor, visibilidade,
associação opcional a indivíduo e timestamps. A entidade reside em `PedigreeProject.annotations`
e não em `Individual`, `Relationship` ou `Parentage`. Portanto, criar ou editar uma nota não
modifica sexo/gênero, fenótipo, parentesco ou análise científica. Referências a indivíduos que
não existem são removidas defensivamente durante validação do documento.

Todas as mutações iniciadas pela interface usam `ReplaceProjectCommand`, oferecendo undo/redo.
O auto-layout opera somente sobre a estrutura familiar. O ajuste à tela pode enquadrar notas
visíveis, o que é intencional para navegação, mas não muda suas coordenadas.

## Testes executados

```text
ruff check .
QT_QPA_PLATFORM=offscreen pytest -q
149 passed
```

A suíte anterior tinha 140 testes. Foram adicionados nove testes da Fase 4.12, cobrindo
neutralidade, monocromia, paleta, criação, atalho, movimentação com undo, persistência,
exportação opt-in, compatibilidade de preferências antigas e contraste dos controles de opção.

## Evidências visuais reais

As imagens abaixo são capturas de widgets PySide6 reais renderizados em modo offscreen, sem
composição artificial:

- `assets/phase_4_12/01_workspace_notes_pt_1920x1080.png`
- `assets/phase_4_12/02_workspace_notes_pt_1366x768.png`
- `assets/phase_4_12/03_phenotype_preferences.png`
- `assets/phase_4_12/04_annotation_editor.png`
- `assets/phase_4_12/05_export_annotation_option.png`
- `assets/phase_4_12/06_workspace_notes_en.png`
- `assets/phase_4_12/07_checkbox_states.png`

O resultado automatizado está em `validation/phase_4_12/validation.json`. Todos os checks
estruturais registrados são verdadeiros.

## Limitações e decisões conscientes

- A associação opcional entre nota e indivíduo está disponível e persistida no modelo; a
  seleção dessa associação ainda não foi exposta no editor visual porque não é necessária ao
  fluxo principal e sua introdução exige uma UX de busca inequívoca.
- Anotações são retangulares e não suportam texto rico. Isso reduz risco de importação e mantém
  SVG/PDF previsíveis.
- Não foram adicionadas novas inferências clínicas nem mudanças no modelo científico de
  sexo/gênero. Os campos legados de cor permanecem exclusivamente para compatibilidade.

## Decisão final

Aceita. Os requisitos centrais da Fase 4.12 estão implementados, os 140 testes históricos foram
preservados, a suíte total passa com 149 testes e as evidências reais confirmam a separação entre
representação científica e comentários visuais.
