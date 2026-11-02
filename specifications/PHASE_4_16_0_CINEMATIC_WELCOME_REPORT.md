# RarePedigree Studio — Fase 4.16.0

## Relatório da Cinematic Welcome Experience

Data de validação: 2 de novembro de 2026.

## Resultado executivo

A tela inicial foi reconstruída dentro da aplicação PySide6 existente, sem criar uma aplicação Web, QML ou fluxo paralelo. A antiga ilustração plana foi substituída por uma **Genomic Sphere** pseudo-3D renderizada com `QPainter`, composta por 74 vértices e 123 conexões estáveis. O componente oferece deformação orgânica, profundidade, rotação, resposta ao cursor, arraste com inércia e pulsação discreta ao clique.

A barra de menu nativa, que aparecia branca sobre a introdução, agora permanece oculta na Welcome Screen e volta a ser exibida ao entrar no editor. Os fluxos Nova família, Abrir projeto e Projetos recentes continuam ligados aos mesmos sinais e serviços anteriores.

Decisão: **fase aceita**. Os requisitos centrais foram implementados e os 183 testes automatizados passam.

## Referência e direção visual

O site público da Nexomic foi consultado apenas como referência conceitual de profundidade, movimento orgânico e linguagem científica. Nenhum código, recurso gráfico ou composição proprietária foi incorporado. A solução final mantém identidade, cores, tipografia, fluxos e arquitetura próprios do RarePedigree Studio.

## Arquitetura escolhida

Foi adotado `QWidget` + `QPainter` por ser a opção mais compatível com a arquitetura atual e com a distribuição desktop existente. A solução não requer OpenGL, navegador embutido ou nova dependência de produção.

O componente `GenomicSphere` mantém uma malha determinística. Os pontos tridimensionais são deformados e rotacionados, projetados com perspectiva e desenhados em ordem de profundidade. A geometria e a lista de arestas são calculadas uma única vez; cada quadro recalcula somente deformação, projeção e pintura.

O modo `fallback_mode` é deliberadamente verdadeiro: a implementação padrão já é o fallback nativo, acelerado o suficiente para o volume atual e compatível com renderização offscreen.

## Parâmetros de animação

| Parâmetro | Padrão | Configuração |
|---|---:|---|
| Limite de FPS | 60 | `welcome/sphere_fps` (15–60) |
| Velocidade orgânica | 0,55 | `welcome/sphere_animation_speed` |
| Deformação | 0,075 | `welcome/sphere_deformation` |
| Frequência espacial | 2,2 | `welcome/sphere_frequency` |
| Rotação automática | 0,16 | `welcome/sphere_rotation_speed` |
| Influência do cursor | 0,20 | `welcome/sphere_cursor_amplitude` |
| Profundidade de perspectiva | 3,4 | `welcome/sphere_depth` |

As configurações são lidas por `QSettings`, permitindo ajustes posteriores sem alterar a estrutura da tela.

## Interações implementadas

- Movimento orgânico contínuo sem alterar a topologia da malha.
- Rotação automática lenta.
- Resposta limitada à posição do cursor.
- Arraste para girar, sem permitir que a esfera invada os cartões.
- Inércia amortecida após o arraste.
- Pulsação de subconjunto de nós após clique curto.
- Microinteração de ícones nos cartões.
- Entrada progressiva da esfera e dos controles.
- Transição curta de opacidade ao entrar no workspace.
- Tema Midnight e tema claro.
- Interface PT-BR e EN.

## Ciclo de vida e acessibilidade

- O timer é iniciado somente quando a Welcome Screen está visível e com movimento habilitado.
- Ao ocultar o widget ou entrar no editor, o timer é interrompido.
- `ui/reduce_motion=true` apresenta a composição final estática, ignora hover/drag e mantém todas as ações funcionais.
- A esfera é marcada com nome acessível como elemento decorativo científico.
- Os cartões mantêm foco, teclado, descrições acessíveis e área de clique completa.
- Os efeitos de opacidade são removidos ao terminar a animação, evitando custo permanente e pintura duplicada.

## Arquivos principais modificados

- `src/rarepedigree/ui/genomic_sphere.py`: novo componente pseudo-3D e suas interações.
- `src/rarepedigree/ui/home.py`: integração da esfera, cabeçalho utilitário, textos institucionais e sequência de entrada.
- `src/rarepedigree/ui/main_window.py`: ocultação do menu na Home e transição para o editor.
- `src/rarepedigree/ui/theme.py`: estilos Midnight/Light da nova composição.
- `src/rarepedigree/ui/i18n.py`: traduções dos novos textos.
- `tests/unit/test_phase_4_16_cinematic.py`: testes específicos da malha, movimento, lifecycle e integração.
- `scripts/validate_phase_4_16_cinematic.py`: capturas, gravação e métricas reproduzíveis.

## Validação automatizada

Comandos executados:

```text
conda run -n rarepedigree-studio ruff check .
QT_QPA_PLATFORM=offscreen conda run -n rarepedigree-studio pytest -q
```

Resultados:

- Ruff: sem erros.
- Pytest: **183 passed in 8.95s**.
- Testes preexistentes preservados: 176.
- Novos testes cinematográficos: 7.
- Testes combinados específicos da Fase 4.16: 19 aprovados.

Os novos testes cobrem determinismo e limites da malha, leitura e clamp de parâmetros, início/parada do timer, movimento reduzido, hover, drag, inércia, pulso, responsividade da projeção, ocultação da barra superior e interrupção da esfera no editor.

## Desempenho medido

Medição offscreen em 1920×1080, sem composição artificial:

| Métrica | Resultado |
|---|---:|
| Construção da janela principal | 71,83 ms |
| Construção até visibilidade | 46,83 ms |
| Animação sem captura concorrente | 57,21 FPS |
| Transição ao editor | 6,94 ms |
| Pico de RSS durante toda a validação/captura | 126,0 MiB |

O valor de FPS inclui o event loop Qt em modo offscreen e se mantém próximo ao limite de 60 FPS. A gravação é produzida a 30 FPS para reduzir tamanho do artefato.

## Evidências reais

Todas as imagens abaixo são `QWidget.grab()` da aplicação real:

- `assets/phase_4_16_0_cinematic/01_pt_midnight_1920x1080.png`
- `assets/phase_4_16_0_cinematic/02_pt_midnight_1366x768.png`
- `assets/phase_4_16_0_cinematic/03_cinematic_entrance.png`
- `assets/phase_4_16_0_cinematic/04_sphere_hover_response.png`
- `assets/phase_4_16_0_cinematic/05_sphere_drag_inertia.png`
- `assets/phase_4_16_0_cinematic/06_sphere_click_pulse.png`
- `assets/phase_4_16_0_cinematic/07_reduced_motion_static.png`
- `assets/phase_4_16_0_cinematic/08_en_light_1920x1080.png`
- `assets/phase_4_16_0_cinematic/09_card_hover_microinteraction.png`
- `assets/phase_4_16_0_cinematic/10_editor_transition.png`

Vídeo real: `assets/phase_4_16_0_cinematic/phase_4_16_0_real_interaction.mp4`, H.264, 1366×768, 30 FPS e 4 segundos.

Métricas estruturadas: `validation/phase_4_16_0_cinematic/validation.json`.

## Compatibilidade e riscos

- Não houve alteração do modelo científico, persistência, editor gráfico ou formatos de projeto.
- Os projetos anteriores continuam usando os mesmos repositórios e fluxos de abertura.
- Os projetos recentes armazenam apenas caminho, título e data; nenhum dado clínico é exibido automaticamente.
- A esfera é pseudo-3D por projeção matemática, não uma cena OpenGL. Isso elimina dependência de driver e reduz risco de empacotamento, mas não oferece iluminação física ou shaders.
- O desempenho visual final deve ainda ser observado em GPUs/monitores de baixa taxa e em sessões remotas; o limite de FPS já pode ser reduzido por configuração.
- Os avisos `propagateSizeHints` observados na plataforma Qt offscreen são limitações do plugin de testes e não aparecem na execução desktop normal.

## Critérios de aceitação

| Critério | Estado |
|---|---|
| Implementação integrada à aplicação atual | Aceito |
| Esfera 3D/pseudo-3D orgânica | Aceito |
| Hover, drag, inércia e clique | Aceito |
| Sem bloqueio dos cartões | Aceito |
| Barra branca removida da introdução | Aceito |
| PT-BR/EN e Midnight/Light | Aceito |
| Movimento reduzido | Aceito |
| Timers interrompidos fora da Home | Aceito |
| 1366×768 e 1920×1080 | Aceito |
| Capturas e vídeo reais | Aceito |
| Fluxos anteriores preservados | Aceito |
| Suíte completa aprovada | Aceito |

