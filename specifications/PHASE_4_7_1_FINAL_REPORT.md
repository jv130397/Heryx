# RarePedigree Studio — Relatório técnico da Fase 4.7.1

Data da validação: 30/10/2026  
Checkpoint anterior às alterações: tag Git `phase-4.7-current-state`, commit `612291d`.

## Resultado executivo

A rodada corrigiu as principais lacunas funcionais da Fase 4.7 sem alterar o esquema dos
projetos: modo Mover real, ferramenta Selecionar não destrutiva, painel esquerdo recolhível,
filtragem semântica dos menus contextuais, fonte/escala efetivas, paletas com prévia,
monocromia, posição da legenda e tradução Qt Linguist em tempo de execução. A linha de base
de 38 testes foi preservada e ampliada para 46 testes.

A fase **não é declarada integralmente concluída** neste relatório. A captura real confirma que
a interface está funcional e mais próxima da referência, mas ainda não atinge fidelidade visual
alta no cabeçalho, nos cartões de propriedades, na tipografia e nas sombras. A cobertura de
internacionalização foi ampliada, porém ainda existem mensagens de erro e alguns rótulos
secundários que precisam ser movidos para o catálogo antes de se aceitar “tradução completa”.

## Matriz de rastreabilidade

| Requisito | Implementação | Teste | Evidência visual | Estado |
|---|---|---|---|---|
| Checkpoint e auditoria | tag `phase-4.7-current-state` em `612291d`; baseline executado | 38/38 no baseline | relatório 4.7 anterior | Aceito |
| Cabeçalho e comandos agrupados | toolbar com marca, projeto e estado; grupos por separadores | smoke de `MainWindow` | `02_workspace_pt_br.png` | Parcial: identidade ainda simplificada |
| Painel esquerdo recolhível | `toggle_tool_rail`, largura 210/60 e mudança de estilo dos botões | `test_tool_rail_collapses_and_expands` | workspace | Aceito |
| Modo Selecionar/Mover | grupo exclusivo; mobilidade dos itens somente em Mover; cursor e drag mode próprios | `test_move_mode_controls_item_mobility` | workspace | Aceito |
| Ações contextuais válidas | ações calculadas pelos pais existentes; não repete pai/mãe nem “pais desconhecidos” | `test_context_actions_filter_existing_parents` | `06_context_menu.png` (popup real) | Aceito |
| Popup dentro da tela | posicionamento delegado ao `QMenu.popup`; captura via tela real | execução do gerador | `06_context_menu.png` | Aceito |
| Cancelamento e undo/redo | diálogo edita cópia; comandos só após aceite | testes existentes de diálogo e comandos | `05_edit_individual.png` | Aceito |
| Tradução `.ts/.qm` | catálogo `rarepedigree_en.ts/.qm`, `QTranslator.load`, retradução de janela e diálogos abertos | mudança sem reinício e diálogo aberto | `03_workspace_en.png` | Parcial: strings secundárias ainda fora do catálogo |
| Fonte e escala | pixel size e geometrias principais derivados de fonte × escala | 100%, 125%, 150% e smoke de DPR | workspaces 1366/1920 | Aceito com limitação: sem matriz física HiDPI |
| Paletas e cores próprias | Scientific, colorblind-safe, high contrast, seletores e restaurar | `test_preferences_palette_preview_and_legend_position` | `07_color_preferences.png` | Aceito |
| Prévia em tempo real | símbolos quadrado/círculo/losango atualizam ao alterar cor ou monocromia | teste de estado da prévia | `07_color_preferences.png` | Aceito |
| Cor versus fenótipo | contorno é decorativo; preenchimento continua fenótipo | teste preexistente preservado | preferências e mono | Aceito |
| Monocromia e exportação independente | chaves `pedigree/monochrome` e `export/monochrome` separadas | teste de restauração pós-exportação | `08` e `09` | Aceito |
| Legenda configurável | posições abaixo, acima e direita; opção de exportação preservada | teste de persistência | workspace/exports | Aceito |
| Modelo sexo/gênero | nenhuma migração; proposta separa sexo, identidade e símbolo | compatibilidade dos 46 testes | não aplicável | Aceito para esta fase |
| Fidelidade visual global | proporções, trilho, canvas, dock e controles aproximados | inspeção das capturas reais | `10`/`11` versus referência | **Não aceito integralmente** |
| Projetos antigos | esquema não alterado; leitores/migrações existentes preservados | suíte de persistência/migração | não aplicável | Aceito |

## Correções implementadas

- O item gráfico não é mais movível no modo Selecionar. Mover ativa a flag Qt apropriada e
  cada deslocamento confirmado continua entrando na pilha de undo/redo.
- O trilho esquerdo alterna entre modo expandido e ícones, mantendo tooltips e nomes
  acessíveis.
- O menu contextual é construído pela mesma função usada pelo evento real e remove ações que
  seriam cientificamente ou estruturalmente redundantes.
- Fonte e escala deixam de ser preferências inertes e alteram fonte, dock e trilho.
- A preferência de tema único deixou de simular uma seleção: “Midnight Genomics” é exibido
  como configuração fixa.
- Paletas, cores próprias, prévia ao vivo, restauração, monocromia e posição da legenda foram
  implementadas sem tocar no estado fenotípico.
- O inglês passou a ser compilado com Qt Linguist. Preferências, editor e assistente conectam-se
  ao sinal de troca de idioma e atualizam botões Salvar/Cancelar enquanto abertos.
- A antiga imagem de menu composta artificialmente foi substituída por captura do popup real.
- A proposta científica de migração foi documentada em
  `SEX_GENDER_REPRESENTATION_MIGRATION_PROPOSAL.md`; nenhuma migração foi aplicada.

## Arquivos de código modificados

- `src/rarepedigree/rendering/items.py`
- `src/rarepedigree/rendering/scene.py`
- `src/rarepedigree/rendering/style.py`
- `src/rarepedigree/ui/dialogs.py`
- `src/rarepedigree/ui/i18n.py`
- `src/rarepedigree/ui/main_window.py`
- `src/rarepedigree/ui/preferences.py`
- `src/rarepedigree/translations/rarepedigree_en.ts`
- `src/rarepedigree/translations/rarepedigree_en.qm`
- `tests/unit/test_main_window.py`
- `tests/unit/test_phase_4_7.py`
- `tools/capture_phase_4_7.py`

## Testes executados

```text
ruff check .
All checks passed!

QT_QPA_PLATFORM=offscreen pytest -q
.............................................. [100%]
46 passed in 1.50s
```

Foram adicionados oito testes, cobrindo modo Mover, recolhimento do trilho, filtragem contextual,
paleta/prévia, posição da legenda, retradução de diálogo aberto e escalas 100/125/150%. O teste
HiDPI atual é um smoke test de `devicePixelRatioF`; não substitui validação em monitores físicos
com fatores de escala distintos.

## Evidências visuais reais

- [Workspace PT-BR](assets/phase_4_7/02_workspace_pt_br.png)
- [Workspace EN](assets/phase_4_7/03_workspace_en.png)
- [Editor flutuante](assets/phase_4_7/05_edit_individual.png)
- [Menu contextual real](assets/phase_4_7/06_context_menu.png)
- [Preferências e prévia de cores](assets/phase_4_7/07_color_preferences.png)
- [Modo monocromático](assets/phase_4_7/08_scientific_monochrome.png)
- [Exportação monocromática](assets/phase_4_7/09_scientific_export.png)
- [Workspace 1366×768](assets/phase_4_7/10_workspace_1366x768.png)
- [Workspace 1920×1080](assets/phase_4_7/11_workspace_1920x1080.png)

O gerador cria widgets reais. No caso do menu, chama `QMenu.popup()` sobre a janela visível e
captura a tela; não há mais composição de pixmaps.

## Comparação com a referência

Elementos agora coerentes: trilho escuro, canvas claro quadriculado, controles flutuantes,
propriedades à direita, barra de projeto/estado, seleção ciano, paleta azul-violeta e hierarquia
canvas/painéis. As proporções em 1366×768 e 1920×1080 permanecem utilizáveis.

Diferenças observadas e não ocultadas:

- o cabeçalho de referência tem logomarca e assinatura em duas linhas; a implementação ainda usa
  uma marca tipográfica compacta;
- os cartões de propriedades da referência têm agrupamento e profundidade mais ricos;
- os ícones atuais são funcionais, porém menos homogêneos que o conjunto visual da referência;
- sombras, raios e densidade tipográfica ainda não alcançam o mesmo acabamento;
- a captura offscreen do popup usa a tela virtual disponível e, por isso, não tem 1366×768.

## Pendências restantes e aceitação

1. Completar a extração de mensagens de erro, notificações e rótulos secundários para `.ts`,
   eliminando o catálogo Python de fallback.
2. Fazer uma rodada visual dedicada ao cabeçalho, cartões, ícones, sombras e tipografia, seguida
   de comparação normalizada com tolerância documentada.
3. Validar 125%, 150% e HiDPI em sessões gráficas reais (não apenas offscreen), incluindo
   inspeção de clipping e navegação por teclado.
4. Adicionar pré-visualização fantasma durante a criação de relações; foi considerada desejável,
   mas não necessária para tornar os comandos atuais corretos.
5. Centralizar a tradução das relações calculadas e mensagens de validação do domínio para não
   expor textos técnicos crus.

Conclusão: requisitos funcionais centrais corrigidos e compatibilidade preservada, mas os critérios
1 (traduções completas) e 8 (proximidade visual alta) ainda têm pendências. Portanto, a Fase 4.7.1
fica **tecnicamente avançada, porém não aceita como concluída** até a próxima rodada de correção.
