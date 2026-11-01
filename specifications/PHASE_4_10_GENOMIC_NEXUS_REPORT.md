# RarePedigree Studio — Fase 4.10

## Genomic Nexus Scientific Workspace

Data: 01/11/2026  
Checkpoint anterior às alterações: `91eadaa`  
Linha de base confirmada: Ruff aprovado e 117 testes aprovados em 3,79 s.

## 1. Resultado

A interface Qt Widgets foi reorganizada como **Genomic Nexus Scientific Workspace**, preservando
`QGraphicsScene/QGraphicsView` e todos os serviços científicos existentes. Nenhum arquivo de
domínio, persistência, comandos de undo/redo ou exportadores foi reescrito nesta fase.

O workspace agora dispõe de minimapa vivo, busca, três modos de visualização, zoom configurável,
foco no probando, exploração de ramos, retorno de navegação, inspector deslizante e preferências
de navegação. O protótipo QML permaneceu isolado e não foi tratado como editor funcional.

Resultado final automatizado: **127 testes aprovados** e **Ruff sem ocorrências**.

## 2. Diagnóstico inicial

- O editor Qt Widgets já possuía rail recolhível, drawer deslizante, tema escuro, auto-layout,
  zoom básico e inspector científico reutilizáveis.
- O `KinshipEngine`, a renderização científica e o layout da Fase 4.9.2 estavam funcionais; a
  suíte real confirmou os 117 testes relatados.
- Não existiam minimapa, busca integrada, modos de visão, foco semântico, exploração por ramos ou
  aviso de legibilidade em visão geral.
- O zoom tinha limites fixos de 20–500%, impedindo uma visão geral de árvores que exigissem menos
  de 20%.
- A interface QML em `ui_next` continua sendo somente um protótipo; não substitui o editor real.

## 3. Arquitetura implementada

### Camada de apresentação

- `ui/workspace.py`: `PedigreeMiniMap`, `IndividualSearch` e `ViewModeControl`.
- `ui/theme.py`: tokens Genomic Nexus centralizados e estados de componentes.
- `rendering/view.py`: zoom configurável, preservação do ponto focal, sinais de viewport e pan.
- `ui/main_window.py`: orquestração de navegação e consumo do `KinshipEngine`.

O minimapa compartilha a `PedigreeScene` real, sem imagem estática ou duplicação do modelo. Busca,
foco e ramos operam sobre UUIDs e arestas do domínio. Coordenadas gráficas nunca são usadas para
inferir parentesco.

### Design system

A paleta aplicada usa Obsidian `#090E1B`, Deep Navy `#111B2E`, Elevated Surface `#17233B`,
Interactive Surface `#22324F`, Electric Cyan `#38BDF8`, Violet `#8B5CF6`, texto `#F8FAFC`,
secundário `#94A3B8`, borda `#30415F` e canvas `#F7FAFF`. O cabeçalho recebeu marca vetorial
renderizada pelo mecanismo SVG já existente.

## 4. Componentes e comportamento verificados

| Requisito | Implementação/evidência | Estado |
|---|---|---|
| Cabeçalho e tool rail | marca, projeto, salvamento, comandos, idioma, modos e ramos | Aceito |
| Canvas científico | cena anterior preservada; grade, pan, seleção e controles flutuantes | Aceito |
| Inspector contextual | drawer sobreposto para pessoa ou parentalidade; não reduz o canvas | Aceito |
| Barra inferior | pessoas, gerações, salvamento, validação e zoom | Aceito |
| Visão geral | `fitInView` sem mínimo artificial; aviso abaixo de 45% configurável | Aceito |
| Visão focada | opacidade por conjunto de UUIDs relacionados | Aceito |
| Visão científica | oculta menu, toolbar, rail, status, minimapa, grade e notificações | Aceito |
| Minimapa | cena real, viewport visível, clique/arraste, atualização e preferência de tamanho | Aceito |
| Zoom inteligente | Ctrl+roda no cursor, botões, atalhos, seleção, fit, 100% e limites | Aceito |
| Foco no probando | núcleo, 2/3 gerações ou todos; cálculo pelo grafo | Aceito |
| Explorador de ramos | materno, paterno, ascendentes, descendentes, irmãos e desconhecidos | Aceito |
| Retorno de navegação | histórico limitado a 20 posições/zooms | Aceito |
| Busca | identificador, UUID avançado, fenótipo e parentesco indexado | Aceito |
| Menus contextuais | ações semânticas para pessoa e área vazia; conexão abre inspector | Aceito |
| Preferências | zoom, legibilidade, minimapa, grade e redução de movimento persistentes | Aceito |
| PT-BR/EN | catálogo Qt recompilado com 142 traduções concluídas | Aceito |
| Exportação limpa | minimapa, grade, busca e chrome são widgets, não itens exportáveis | Aceito |

## 5. Busca e performance

A primeira medição materializava todos os resultados e calculava parentesco repetidamente: a
busca em 200 pessoas chegou a aproximadamente 976 ms. A implementação foi corrigida com índice de
parentesco por projeto e paginação visual de resultados. A busca continua percorrendo o conjunto
completo, mas cria no máximo 50 itens visuais por consulta.

Metodologia: Linux x86_64, Qt offscreen, `perf_counter` em operações síncronas; RSS é o pico do
processo completo durante a execução acumulada. Os valores reproduzíveis ficam em
`validation/phase_4_10/validation.json`.

| Pessoas | Inicialização ms | Layout ms | Carga ms | Fit ms | Seleção ms | Busca ms | Minimap ms | Pico RSS KiB |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 26,3 | 1,7 | 7,3 | 0,9 | 3,3 | 0,22 | 0,12 | 289.204 |
| 50 | 24,6 | 1,8 | 7,8 | 1,0 | 3,7 | 0,24 | 0,11 | 293.940 |
| 100 | 27,4 | 5,7 | 19,9 | 1,0 | 7,3 | 0,27 | 0,17 | 303.540 |
| 200 | 25,2 | 20,0 | 49,6 | 1,4 | 22,9 | 0,45 | 0,36 | 315.444 |

Esses números são uma amostra do ambiente indicado, não garantias universais. Zoom e pan foram
verificados funcionalmente; uma medição objetiva de taxa de quadros depende de execução em uma
plataforma gráfica real e não foi inventada.

## 6. Testes

```text
conda run -n rarepedigree-studio ruff check .
All checks passed!

QT_QPA_PLATFORM=offscreen conda run -n rarepedigree-studio pytest -q
127 passed
```

Os 10 testes novos cobrem minimapa real, navegação, busca por label/UUID, inspector, foco por
grafo, ramos materno/paterno, visão científica, zoom e limites, preferências, menus semânticos e
busca em 200 indivíduos. Os 117 testes científicos e de interface anteriores foram preservados.

## 7. Evidências visuais reais

As 15 imagens foram geradas por `QWidget.grab()` do aplicativo real, sem composição artificial:

1. [Workspace sem seleção](assets/phase_4_10/01_workspace_no_selection.png)
2. [Seleção e inspector](assets/phase_4_10/02_selected_inspector.png)
3. [Busca integrada](assets/phase_4_10/03_search.png)
4. [Foco no probando](assets/phase_4_10/04_focus_proband.png)
5. [Ramo materno](assets/phase_4_10/05_maternal_branch.png)
6. [Ramo paterno](assets/phase_4_10/06_paternal_branch.png)
7. [Minimapa vivo](assets/phase_4_10/07_live_minimap.png)
8. [Visão geral de 50 pessoas](assets/phase_4_10/08_overview_50.png)
9. [Visão focada da mesma família](assets/phase_4_10/09_focused_50.png)
10. [Visão científica](assets/phase_4_10/10_scientific_view.png)
11. [PT-BR em 1366×768](assets/phase_4_10/11_pt_1366x768.png)
12. [PT-BR em 1920×1080](assets/phase_4_10/12_pt_1920x1080.png)
13. [Inglês em 1366×768](assets/phase_4_10/13_en_1366x768.png)
14. [Inglês em 1920×1080](assets/phase_4_10/14_en_1920x1080.png)
15. [Tool rail recolhida](assets/phase_4_10/15_collapsed_rail.png)

Em comparação com a Fase 4.9.2, a árvore de 50 pessoas continua cientificamente idêntica, mas
agora possui visão geral sem bloqueio de escala, aviso de legibilidade, minimapa, busca, foco e
inspector sobreposto. A inspeção das primeiras capturas encontrou e corrigiu minimapa atrás do
canvas, busca sem altura útil e evidência do inspector capturada durante a animação.

## 8. Arquivos principais

- `src/rarepedigree/ui/workspace.py` (novo)
- `src/rarepedigree/ui/main_window.py`
- `src/rarepedigree/ui/theme.py`
- `src/rarepedigree/ui/preferences.py`
- `src/rarepedigree/ui/i18n.py`
- `src/rarepedigree/ui/icons.py`
- `src/rarepedigree/rendering/view.py`
- `src/rarepedigree/rendering/scene.py`
- `src/rarepedigree/rendering/items.py`
- `src/rarepedigree/translations/rarepedigree_en.ts/.qm`
- `tests/unit/test_phase_4_10.py` (novo)
- `scripts/validate_phase_4_10.py` (novo)

## 9. Limitações e recomendações

1. O modelo atual possui identificador exibido, mas não um campo independente de nome civil; a
   busca não inventa esse dado. Um futuro campo opcional deve ser adicionado por migração de schema.
2. O benchmark offscreen mede latência de operações, não FPS real de GPU. Recomenda-se um perfil
   complementar em Wayland/X11 nos equipamentos clínicos suportados.
3. Árvores extensas ainda dependem de zoom/foco para leitura de rótulos; isso é explicitamente
   sinalizado em vez de ocultar indivíduos.
4. O protótipo QML permanece não funcional e não deve receber regras científicas duplicadas.
5. Uma futura fase pode acrescentar paginação explícita à busca e atalhos configuráveis, sem
   modificar o motor científico.

## 10. Aceitação

A Fase 4.10 é **aceita** para o workspace Qt Widgets. O minimapa navega na cena real; busca, zoom,
foco, ramos e inspector funcionam; PT-BR/EN e resoluções-alvo foram capturados; exportações não
recebem elementos do workspace; 200 pessoas permanecem navegáveis nas medições realizadas; e a
suíte científica anterior permanece integralmente aprovada.
