# RarePedigree Studio — Fase 4.8
## Genomic Nexus UI 2.0

Data: 30/10/2026  
Checkpoint anterior: tag `phase-4.7.1`, commit `39d727b`.

## Resultado

Foi implementado um protótipo Qt Quick/QML independente em `rarepedigree.ui_next`. A interface
anterior e seu ponto de entrada não foram substituídos. O protótipo apresenta uma família sintética
de três gerações, seleção, propriedades, zoom/pan, editor modal, undo/redo, PT-BR/EN e cores de
representação. O domínio Pydantic, `FamilyService`, layout e preferências existentes permanecem
a fonte de verdade.

Execução independente:

```bash
python -m rarepedigree.ui_next
```

## Auditoria e ambiente

- Python: 3.12 no ambiente Conda `rarepedigree-studio`.
- PySide6: 6.10.3.
- Qt: 6.10.3.
- Disponíveis e verificados: QtQml, QtQuick, `QQmlApplicationEngine`, `QQuickItem`,
  `QQuickPaintedItem`, Qt Quick Controls e registro de tipos QML.
- Nenhuma dependência foi instalada.
- Baseline da Fase 4.7.1: 46 testes aprovados.
- Resultado atual: 52 testes aprovados.

Serviços reutilizados: `PedigreeProject`, `Individual`, estados científicos, `FamilyService`,
`PedigreeLayoutEngine`, `PedigreeRenderStyle`, `QSettings`, `LanguageManager` e `QUndoStack`.
Persistência, migrações e exportadores antigos não foram alterados.

## Prova de viabilidade do canvas

### Estratégia A — renderer QML alimentado por Python

Foi a estratégia escolhida para o protótipo. `PeopleModel`, um `QAbstractListModel`, projeta o
projeto Python sem copiá-lo. `PedigreeCanvas.qml` desenha grade e conectores; `PersonNode.qml`
desenha quadrado, círculo e losango com preenchimento fenotípico independente do contorno.
Seleção volta ao controller por Slot.

Vantagens observadas: bindings declarativos, animações simples, componentes reutilizáveis e boa
latência com 100 indivíduos. Riscos: o roteamento atual de conectores é uma prova de conceito e
ainda não reproduz todas as convenções do renderer QGraphics.

### Estratégia B — incorporar o renderer Qt existente

Descartada para o protótipo. `QGraphicsView` é widget-based e não se integra diretamente à árvore
de cena Qt Quick. Uma camada de textura/window container adicionaria complexidade de foco, popup,
HiDPI e eventos, com pouca vantagem visual.

### Estratégia C — renderer híbrido

Recomendada como etapa seguinte: manter o canvas QML para interação, mas extrair do renderer atual
uma descrição gráfica Python compartilhada para conectores, gêmeos, adoção, consanguinidade e
exportação. Isso reduz divergência sem tentar incorporar `QGraphicsView`.

## Arquitetura

```text
ui_next/app.py
  └─ QQmlApplicationEngine
     ├─ NexusController (projeto, comandos, idioma, preferências)
     ├─ PeopleModel (QAbstractListModel; projeção sem segunda fonte de verdade)
     └─ qml/Main.qml
        ├─ theme/NexusTheme.qml
        ├─ canvas/PedigreeCanvas.qml + PersonNode.qml
        ├─ panels/PropertiesPanel.qml
        └─ dialogs/PersonEditor.qml + NexusPreferences.qml
```

As mutações não ocorrem em QML. Confirmar o editor chama `updateSelected`, que cria um
`QUndoCommand`; cancelar fecha o diálogo sem chamada ao controller. Cores atualizam
`PedigreeRenderStyle` e são persistidas nas mesmas chaves `QSettings` da interface atual.

## Design system e componentes

`NexusTheme.qml` implementa os tokens especificados: fundos `#090E1B/#111B2E`, superfícies
`#17233B/#22324F`, ciano `#38BDF8`, violeta `#8B5CF6`, rosa `#EC4899`, texto e bordas.
O protótipo inclui cabeçalho, trilho animado, canvas claro, zoom flutuante, propriedades,
statusbar, botões com hover, editor e preferências. As transições usam 140–170 ms.

Controles sem integração nesta prova — adicionar, relações, mover, excluir, auto-layout manual e
exportar — aparecem desabilitados/experimentais, e não simulam funcionalidade.

## Funcionalidades verificadas

- inicialização independente do engine QML;
- família sintética de cinco indivíduos e três gerações;
- seleção atualiza resumo e painel de propriedades;
- editor modal com foco, Escape, confirmar/cancelar;
- alteração real de identificador, fenótipo e falecimento;
- undo/redo da edição;
- zoom e pan pelo `Flickable`, roda e controles;
- troca PT-BR/EN em execução;
- paletas e cores próprias, monocromia e persistência;
- menu contextual QML real, com ações não integradas desabilitadas;
- painel esquerdo recolhível com animação.

## Testes

```text
ruff check .
All checks passed!

QT_QPA_PLATFORM=offscreen pytest -q
.................................................... [100%]
52 passed
```

Os seis testes novos cobrem engine QML, canvas, projeção do projeto, três gerações, seleção,
edição, cancelamento, undo/redo, idioma e cores. Os 46 testes anteriores permanecem aprovados.

## Performance

Medições executadas com `QT_QPA_PLATFORM=offscreen`, Linux, Python 3.12, Qt 6.10.3, no mesmo
processo. Cada tamanho foi carregado em um engine novo; o primeiro inclui aquecimento de QML.

| Indivíduos | Controller | Engine QML | Seleção mediana | Pico RSS do processo |
|---:|---:|---:|---:|---:|
| 10 | 0,224 ms | 118,357 ms | 0,3881 ms | 123168 KiB |
| 30 | 0,236 ms | 29,212 ms | 0,5204 ms | 124320 KiB |
| 100 | 0,206 ms | 38,499 ms | 0,8506 ms | 129748 KiB |

O RSS é cumulativo/pico do processo e não deve ser interpretado como consumo isolado de cada
família. O benchmark reproduzível está em `tools/benchmark_ui_next.py`; os dados brutos estão em
`assets/phase_4_8/performance.json`. “Fluidez” foi avaliada indiretamente por latência; testes de
frame pacing em GPU real continuam pendentes.

## Evidências visuais reais

- [Tela inicial PT-BR](assets/phase_4_8/01_initial_pt_br.png)
- [Workspace com três gerações](assets/phase_4_8/02_three_generations.png)
- [Indivíduo selecionado](assets/phase_4_8/03_individual_selected.png)
- [Editor flutuante](assets/phase_4_8/04_person_editor.png)
- [Menu contextual](assets/phase_4_8/05_context_menu.png)
- [Preferências](assets/phase_4_8/06_preferences.png)
- [Workspace PT-BR](assets/phase_4_8/07_workspace_pt_br.png)
- [Workspace em inglês](assets/phase_4_8/08_workspace_en.png)
- [1366×768](assets/phase_4_8/09_workspace_1366x768.png)
- [1920×1080](assets/phase_4_8/10_workspace_1920x1080.png)

As imagens foram obtidas da janela Qt Quick real por `QScreen.grabWindow`; editor, menu e
preferências são overlays reais, não composições.

## Comparação com a interface atual

O Genomic Nexus apresenta cabeçalho mais claro, marca e projeto separados, hierarquia espacial
mais consistente, trilho animado, modal integrado ao workspace, tokens centralizados e bindings
de estado nativos. A interface widget atual continua superior em completude científica e edição
de estrutura familiar. Portanto, o protótipo demonstra melhora visual, mas ainda não justifica
substituição do editor atual.

## Limitações e riscos

1. Conectores QML são POC: uniões de irmãos, gêmeos, adoção, consanguinidade e separação ainda
   precisam da geometria científica compartilhada.
2. Exportação continua disponível apenas na interface atual; o botão Nexus está desabilitado.
3. Adição, relações, mover e excluir ainda não foram conectados.
4. A tradução QML usa uma ponte pequena; a migração futura deve usar catálogos Qt Linguist
   gerados também a partir de `qsTr`.
5. O estilo de controles nativos varia por plataforma e requer normalização adicional.
6. Redução de movimento ainda não é detectada automaticamente.
7. Performance deve ser repetida em sessão gráfica real com medição de FPS/frame time.

## Recomendação de migração

Não substituir `ui/` neste momento. Avançar incrementalmente com a estratégia C: extrair um
modelo de geometria de heredograma independente de toolkit, usado por QGraphics, QML e
exportadores; depois integrar comandos estruturais um por um. Manter ambos os pontos de entrada
até paridade de testes científicos, acessibilidade, exportação e desempenho em GPU real.

## Aceitação

O protótipo satisfaz os critérios de aceitação da prova experimental: inicia separadamente, não
altera a interface antiga, preserva o núcleo, apresenta a família, seleção e editor funcionais,
troca idioma e cores, mantém todos os testes e documenta a estratégia. Ele **não é declarado
substituto de produção**; as limitações acima definem o gate para uma migração futura.
