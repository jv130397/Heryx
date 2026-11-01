# Fase 4.10.2 — Visual Excellence & Scientific UI

## Resultado executivo

A pasta `Modelos/` foi reavaliada integralmente. Além do vídeo conhecido, foram encontradas dez novas capturas Full HD que documentam editor pessoal/clínico, ações contextuais, dropdown, configuração de rótulos, testes clínicos, exportação e paleta de condições. A implementação combinou os padrões compatíveis com o RarePedigree sem copiar marcas ou introduzir campos clínicos ainda não suportados.

Foram corrigidos os rótulos truncados do rail compacto, reorganizados seus grupos, refinadas toolbar e grade, adicionadas superfícies próprias de importação/exportação e criada numeração genealógica puramente apresentacional. O domínio, o motor de parentesco e os dados persistidos não foram modificados.

## Referências e comparação

O inventário com caminho, tamanho, data, hash, formato e análise individual está em [PHASE_4_10_2_MODELS_AUDIT.md](PHASE_4_10_2_MODELS_AUDIT.md).

| Aspecto | Fase 4.10.1 | Novas referências | Fase 4.10.2 |
|---|---|---|---|
| Rail compacto | Dois `QAction` podiam perder o ícone após retradução e mostrar texto truncado | Controles compactos são exclusivamente icônicos | Ícones pertencem aos próprios `QAction`; zero rótulo no compacto |
| Organização do rail | Sequência contínua | Ferramentas agrupadas e destruição separada | Edição, Organização e Excluir no rodapé |
| Rótulos | Apenas identificador manual | Modal mostra numeração `I-1`, `II-3` | Manual, genealógico ou combinado, sem alterar dados |
| Importar/exportar | Seletor nativo direto | Modais proporcionais com cabeçalho e opções | Superfícies Genomic Nexus antes do seletor de arquivo |
| Grade | Passo fixo em qualquer zoom | Canvas quase neutro | 40/80 unidades e ocultação abaixo de 30% |
| Preferências | Página extensa sem rolagem | Modal organizado por seções | Aba Heredograma rolável |
| Movimento | Drawer a 180 ms | Expansões rápidas e discretas | Rail 160 ms e drawer 180 ms; redução de movimento respeitada |

## Design system consolidado

O [GENOMIC_NEXUS_DESIGN_SYSTEM.md](GENOMIC_NEXUS_DESIGN_SYSTEM.md) foi atualizado. `ui/theme.py` agora centraliza cores, espaçamentos, raios, movimento, tipografia, ícones, controles, elevação e breakpoints. Os valores principais permanecem superfície branca, canvas `#F1F3F5`, estrutura `#1C293B`, interação `#078FC2` e texto `#1F2933`.

## Componentes modificados

- `rendering/items.py`: rótulo gráfico separado de `Individual.label`.
- `rendering/scene.py`: cálculo determinístico de numeração por geração e ordem horizontal.
- `rendering/view.py`: grade adaptativa ao zoom.
- `ui/main_window.py`: rail agrupado, ícones persistentes, animação, importação/exportação e retradução.
- `ui/dialogs.py`: modais de importar/exportar e cabeçalhos proporcionais.
- `ui/preferences.py`: modo de identificador e rolagem na página extensa.
- `ui/components.py`: cabeçalho modal com altura fixa.
- `ui/workspace.py`: viewport do minimapa com ciano do design system.
- `ui/i18n.py`: traduções dos novos componentes e ações principais.
- `ui/theme.py`: novos tokens e separador do rail.

## Identificadores

O caso “indivíduo da geração III exibido como `I-2`” era ambíguo porque o sistema tratava `label` como texto manual, não como numeração calculada. A solução preserva compatibilidade:

1. UUID continua sendo a chave interna imutável.
2. `Individual.label` continua sendo o identificador manual persistido.
3. A numeração genealógica é recalculada somente na cena: geração em algarismo romano e posição horizontal iniciada em 1.
4. A preferência `pedigree/identifier_mode` oferece `manual`, `genealogical` e `both`.

Nenhum projeto antigo é migrado ou renomeado.

## Validação visual

A rotina `scripts/validate_phase_4_10_2.py` gera widgets Qt reais, sem mockups, e registra os resultados em `validation/phase_4_10_2/validation.json`.

Evidências obrigatórias:

- [Workspace 1920×1080](assets/phase_4_10_2/01_workspace_1920x1080.png)
- [Workspace 1366×768](assets/phase_4_10_2/02_workspace_1366x768.png)
- [Rail compacto](assets/phase_4_10_2/03_rail_compact.png)
- [Rail expandido](assets/phase_4_10_2/04_rail_expanded.png)
- [Dropdown](assets/phase_4_10_2/05_family_dropdown.png)
- [Menu contextual](assets/phase_4_10_2/06_context_menu.png)
- [Inspector](assets/phase_4_10_2/07_inspector.png)
- [Modal de edição](assets/phase_4_10_2/08_edit_modal.png)
- [Modal de familiar](assets/phase_4_10_2/09_relative_modal.png)
- [Importação](assets/phase_4_10_2/10_import_modal.png)
- [Exportação](assets/phase_4_10_2/11_export_modal.png)
- [Preferências e rótulos](assets/phase_4_10_2/12_preferences_labels.png)
- [Minimapa](assets/phase_4_10_2/13_minimap.png)
- [Quatro gerações](assets/phase_4_10_2/14_four_generations.png)
- [50 indivíduos](assets/phase_4_10_2/15_family_50.png)
- [100 indivíduos](assets/phase_4_10_2/16_family_100.png)
- [Interface em inglês](assets/phase_4_10_2/17_workspace_en.png)

### Inspeção explícita

- Rail compacto: nenhum texto, abreviação ou elipse; ícones centralizados e estados ativos visíveis.
- Rail expandido: rótulos completos dentro de 210 px; separador e alinhamento consistentes.
- Modais: cabeçalho de 66 px, campos e ações visíveis; importação/exportação abaixo de 700 px de largura.
- Inspector: sobreposto, rolável, sem redução permanente do canvas.
- Grade: discreta e ausente no overview muito reduzido.
- Minimapa: moldura estável, viewport ciano e ausência nas exportações.
- Inglês: menus, toolbar, status e valores principais retraduzidos em runtime; toast anterior é descartado na troca.

## Testes

Linha de base: 128 testes. Resultado final:

```text
conda run -n rarepedigree-studio ruff check .
All checks passed!

QT_QPA_PLATFORM=offscreen conda run -n rarepedigree-studio pytest -q
131 passed
```

Os três testes novos cobrem numeração apresentacional sem mutação, persistência da preferência e proporções das superfícies de importação/exportação. O teste do rail também passou a verificar explicitamente `ToolButtonIconOnly` e `ToolButtonTextBesideIcon`.

## Limitações e pendências reais

1. O ambiente disponível não expõe sessão gráfica Ubuntu real. As capturas são renderizações Qt `offscreen`; X11, Wayland, compositor, foco de teclado e HiDPI físico permanecem pendentes de verificação manual.
2. Qt Widgets não oferece animação nativa segura para `QMenu` em todas as combinações X11/Wayland. Os menus usam comportamento nativo imediato para preservar foco e clique; rail e drawer possuem transições controladas.
3. A referência mostra HPO, testes genéticos e formatos clínicos ainda não suportados. Eles não foram apresentados como funcionais nem adicionados ao modelo nesta fase.
4. O cálculo genealógico usa ordem horizontal atual; mover manualmente e recarregar a cena pode alterar a numeração, como esperado para um rótulo calculado e não persistido.

## Decisão de aceitação

| Critério | Estado |
|---|---|
| Novas referências auditadas | Aceito |
| Inventário e hashes | Aceito |
| Rail sem texto truncado | Aceito |
| Tipografia/tokens consolidados | Aceito |
| Dropdowns, modais e inspector | Aceito |
| Grade e minimapa | Aceito |
| IDs separados da genealogia | Aceito |
| PT-BR/EN no escopo funcional | Aceito |
| Testes científicos | Aceito — 131 testes |
| Evidências reais de widgets | Aceito |
| X11/Wayland/HiDPI físico | Pendente por indisponibilidade do ambiente |

A implementação e a validação automatizada da Fase 4.10.2 estão concluídas. A aceitação gráfica de plataforma permanece condicionada a uma rodada manual em X11 e Wayland; o relatório não afirma que essa validação indisponível foi executada.
