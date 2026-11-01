# Fase 4.10.1 — Relatório de reconstrução orientada pelo modelo

## Resultado executivo

A referência foi efetivamente localizada em `Modelos/heredograma_linkedin.mp4`, auditada quadro a quadro e usada como fonte principal da reconstrução. O RarePedigree Studio adotou o shell clínico claro, cabeçalhos azul-marinho, superfícies compactas, navegação lateral estreita, menus brancos e overlays observados no vídeo, sem copiar código, marcas ou ativos do Open Pedigree X/PhenoTips.

A estratégia escolhida foi **Qt Widgets modernizado**. O `QGraphicsScene/QGraphicsView`, o motor de parentesco, layout, persistência, undo/redo e exportadores não foram substituídos. A suíte final tem **128 testes aprovados**.

## Auditoria e decisão arquitetural

O inventário, metadados, quadros amostrados, limitações e matriz de diferenças estão em [MODEL_REFERENCE_AUDIT.md](MODEL_REFERENCE_AUDIT.md). A pasta contém um único vídeo H.264 de 46,1 s, 1280×720 e 30 fps; não contém fontes, código, licenças ou especificações de animação. PyAV foi usado isoladamente em `/tmp` para extrair os quadros, sem alterar o ambiente do projeto.

O material mostra uma aplicação web científica clara: canvas cinza, toolbar branca compacta, navegação flutuante, overlays de pesquisa, modais com cabeçalho escuro e formulários densos. Como o editor atual já é estável em Qt Widgets, migrar para QML introduziria duas interfaces e risco científico sem benefício proporcional.

## Matriz de reconstrução

| Componente anterior | Referência observada | Solução entregue | Estado |
|---|---|---|---|
| Shell predominantemente escuro | Superfícies clínicas claras | Tokens e QSS claros centralizados | Aceito |
| Barra lateral larga | Navegação compacta flutuante | 60 px por padrão, 210 px expandida | Aceito |
| Inspector denso | Painel contextual organizado | Drawer sobreposto, rolável, abas e cartões | Aceito |
| Formulários sem identidade modal | Cabeçalho escuro e corpo branco | `NexusDialogHeader` reutilizável | Aceito |
| Menus com acabamento inconsistente | Dropdown branco compacto | `QMenu`/`FamilyMenu` com seleção ciano | Aceito |
| Canvas quase branco | Cinza claro com grade discreta | `#F1F3F5` e grade `#DDE2E6` | Aceito |
| Ícones claros sobre fundos variados | Ícones escuros em toolbar clara | SVGs internos com `#334155` | Aceito |
| Relações em texto corrido | Blocos de informação | Cartões compactos e roláveis | Aceito |
| Textos parciais no novo UI | PT-BR/EN em runtime | Catálogo ampliado; chaves internas estáveis | Aceito no escopo alterado |

## Componentes modificados

- `ui/theme.py`: tokens, tipografia, estados, campos, menus, tabs, cards, modais e overlays.
- `ui/components.py`: cabeçalho modal reutilizável e drawer com rolagem e sombra discreta.
- `ui/main_window.py`: rail compacto por padrão e alternância expansível.
- `ui/dialogs.py`: cabeçalhos e hierarquia visual em edição, criação e parentesco.
- `ui/properties.py`: resumo e relações em cartões; traduções de conteúdo calculado.
- `ui/icons.py`: cor-base adequada a superfícies claras.
- `rendering/scene.py` e `rendering/view.py`: fundo e grade alinhados ao modelo.
- `ui/i18n.py`: novas strings PT-BR/EN, sem traduzir enums persistidos.

O sistema visual resultante está especificado em [GENOMIC_NEXUS_DESIGN_SYSTEM.md](GENOMIC_NEXUS_DESIGN_SYSTEM.md).

## Integridade científica

Não houve mudança no domínio nem no motor de parentesco. Símbolo, fenótipo, probando, falecimento, parentalidade, adoção, gêmeos, consanguinidade e núcleos parentais continuam sendo renderizados pelo estilo científico existente. A cor ciano da interface indica foco/ação; não redefine estado clínico. O modo monocromático e as opções independentes de exportação foram preservados.

## Testes e desempenho

Comandos finais:

```text
conda run -n rarepedigree-studio ruff check .
QT_QPA_PLATFORM=offscreen conda run -n rarepedigree-studio pytest -q
conda run -n rarepedigree-studio python scripts/validate_phase_4_10.py
conda run -n rarepedigree-studio python scripts/validate_phase_4_10_1.py
```

Resultado: Ruff sem ocorrências e **128 passed**. Foram mantidos os testes científicos e adicionada verificação do cabeçalho semântico. Os testes de workspace agora verificam explicitamente o novo rail compacto e sua expansão; essa atualização registra uma mudança intencional do requisito, não oculta regressão.

Na medição anterior à rodada final, 200 indivíduos foram posicionados em 19,1 ms, carregados em 48,7 ms, pesquisados em 0,35 ms e atualizados no minimapa em 0,26 ms. A validação final mede 4, 20, 50, 100 e 200 indivíduos e está registrada em `validation/phase_4_10/validation.json`.

## Evidências reais

Todas as imagens abaixo são capturas de widgets Qt reais; não são mockups nem composições:

- [Workspace PT-BR](assets/phase_4_10_1/01_workspace_pt.png)
- [Inspector deslizante](assets/phase_4_10_1/02_inspector_drawer.png)
- [Popover de busca](assets/phase_4_10_1/03_search_popover.png)
- [Dropdown de familiares](assets/phase_4_10_1/04_family_dropdown.png)
- [Modal de edição](assets/phase_4_10_1/05_edit_individual_modal.png)
- [Modal de irmão](assets/phase_4_10_1/06_add_sibling_modal.png)
- [Novo projeto](assets/phase_4_10_1/07_new_project_modal.png)
- [Preferências](assets/phase_4_10_1/08_preferences.png)
- [Workspace em inglês](assets/phase_4_10_1/09_workspace_en.png)
- [1366×768 PT-BR](assets/phase_4_10/11_pt_1366x768.png)
- [1920×1080 PT-BR](assets/phase_4_10/12_pt_1920x1080.png)
- [Família de 50 indivíduos](assets/phase_4_10/08_overview_50.png)

Os quadros usados como referência estão em `assets/model_reference/`; a captura `frame_025_00s.png` documenta o workspace e `frame_040_00s.png` o modal de exportação.

## Limitações verificadas

1. O vídeo é promocional e contém cortes; durações exatas de todas as animações não podem ser inferidas. Foi adotada a faixa de 120–220 ms da especificação, com drawer a 180 ms.
2. A execução automatizada ocorreu com o plugin Qt `offscreen`. X11, Wayland e comportamento do compositor precisam de uma sessão gráfica real para validação conclusiva.
3. Diálogos nativos de arquivo para importar/exportar dependem do desktop e não foram automatizados visualmente; os exportadores continuam cobertos por testes funcionais.
4. A imagem de 100 indivíduos usa a evidência de desempenho e navegação da Fase 4.10; a interface permanece a mesma, mas a legibilidade global deliberadamente exige busca/foco em zoom muito baixo.
5. Não foi reproduzida marca, tipografia proprietária ou ativo do produto mostrado na referência por ausência de licença explícita.

## Aceitação

| Critério | Resultado |
|---|---|
| Pasta de modelo analisada | Aceito |
| Arquitetura e restrições documentadas | Aceito |
| Paleta, proporções e hierarquia alinhadas | Aceito |
| Dropdowns e modais consistentes | Aceito |
| Inspector reorganizado | Aceito |
| Texto novo traduzido em runtime | Aceito |
| Canvas e motor científico preservados | Aceito |
| Testes automatizados | Aceito |
| Evidência visual real | Aceito |
| X11/Wayland em hardware real | Pendente de validação manual |

A reconstrução de código está concluída. A aprovação visual definitiva deve incluir uma curta rodada manual em X11 e Wayland, especialmente para sombras, menus nativos e escala HiDPI; essa limitação de ambiente não foi apresentada como validação realizada.
