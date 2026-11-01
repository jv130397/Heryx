# Auditoria da referência visual — Fase 4.10.1

Data: 01/11/2026  
Pasta solicitada: `modelo`  
Pasta localizada: `Modelos/`

## 1. Estrutura encontrada

```text
Modelos/
└── heredograma_linkedin.mp4
```

A pasta contém somente um vídeo. Não há código-fonte, HTML, CSS, JavaScript, TypeScript, React,
Vue, Python, Qt Widgets, QML, imagens separadas, SVGs, fontes, README, manifesto, dependências ou
instruções de execução. O MP4 é a referência principal; não existem recursos auxiliares dentro da
pasta.

## 2. Características técnicas verificadas

| Propriedade | Valor |
|---|---|
| Contêiner | MPEG-4 |
| Codec | H.264 |
| Perfil visual decodificado | YUV 4:2:0 |
| Duração | 46.100 ms |
| Resolução | 1280×720 |
| Taxa média | 30 fps |
| Tamanho | 1.208.437 bytes |

O arquivo foi inspecionado de forma somente leitura. Como `ffmpeg` não estava instalado e o
backend Qt Multimedia não entregou quadros em modo offscreen, a extração foi feita com o wheel
PyAV instalado isoladamente em `/tmp` via `pip --target`. O ambiente Conda e a pasta `Modelos`
não foram modificados. O procedimento reproduzível está em `scripts/audit_model_reference.py`.

Metadados e quadros: `specifications/assets/model_reference/`.

## 3. Produto e componentes observáveis

O vídeo identifica a referência como **Open Pedigree X 1.3**, com menção a tecnologia PhenoTips.
Os estados observáveis são:

1. tela de título;
2. workspace com modal de boas-vindas em três cartões;
3. heredograma com cabeçalho científico e legenda lateral;
4. painel suspenso de busca com filtros combináveis e resultados;
5. modal grande de teste em cascata com formulário e tabela;
6. modo de destaque de parentes com legenda flutuante inferior;
7. anotação livre diretamente sobre o heredograma;
8. modal de exportação com rádio, checkboxes e selects.

Quadros principais:

- [Boas-vindas](assets/model_reference/frame_01_005767ms.png)
- [Workspace científico](assets/model_reference/frame_02_011533ms.png)
- [Busca e filtros](assets/model_reference/frame_03_017300ms.png)
- [Modal/tabela](assets/model_reference/frame_04_023033ms.png)
- [Destaque científico](assets/model_reference/frame_05_028800ms.png)
- [Anotação](assets/model_reference/frame_06_034567ms.png)
- [Exportação](assets/model_reference/frame_07_040333ms.png)

## 4. Linguagem visual extraída

### Paleta observável

Os valores são aproximações medidas nos quadros comprimidos; o vídeo não fornece tokens-fonte.

- canvas: cinza muito claro, aproximadamente `#E8E8E8`;
- superfícies: branco/quase branco, `#F8F8F8`;
- cabeçalhos de modal e cápsulas: navy, aproximadamente `#182030`–`#202838`;
- texto principal: carvão, próximo de `#202830`;
- texto secundário: cinza médio;
- ação/seleção: azul-ciano, aproximadamente `#078FC2`;
- bordas: cinza claro, discretas;
- backdrop: cinza azulado semitransparente;
- alertas científicos: vermelho, azul, verde e amarelo, usados como dados e não como decoração.

### Tipografia

A fonte exata não é determinável pelo vídeo. A aparência é de sans-serif de interface, com:

- corpo aproximado de 13–15 px;
- controles 13–14 px;
- títulos de modal 16–18 px, semibold/bold;
- título científico 17–19 px;
- captions promocionais 22–28 px;
- altura de linha compacta, porém legível.

Nenhum arquivo de fonte ou licença de fonte foi fornecido. A reconstrução deverá usar a pilha
nativa Inter/Noto Sans/Segoe UI já adotada, sem incorporar fonte externa.

### Geometria

- toolbar horizontal branca, aproximadamente 36–40 px de altura;
- grupos de comandos separados por linhas verticais;
- navegação flutuante à esquerda, não uma rail larga permanente;
- modais centrados de 600–960 px, cabeçalho navy de cerca de 44 px;
- raio discreto de aproximadamente 8–12 px;
- sombra ampla e suave;
- campos de 32–36 px;
- botões primários azul-ciano e secundários neutros;
- search sheet de aproximadamente 450 px, alinhada ao topo/esquerda;
- formulários densos, com espaços de 8–16 px;
- canvas ocupa quase todo o viewport.

### Comportamentos observáveis

- backdrop reduz a ênfase do canvas quando um modal está ativo;
- painéis de busca flutuam sobre o heredograma sem redimensioná-lo;
- filtros são adicionados em linhas, com selects e remoção individual;
- seleção científica usa anéis coloridos e esmaecimento dos demais;
- ações analíticas podem resultar em uma barra/legenda flutuante inferior;
- diálogos usam cabeçalho fixo com botão fechar;
- toolbar e menus têm densidade alta e hierarquia por agrupamento.

O vídeo contém cortes promocionais. Ele não permite medir de forma confiável curvas, duração ou
quadros intermediários das animações. Não há evidência suficiente para alegar transições exatas;
a reconstrução usará 160–180 ms, dentro do intervalo da especificação, e respeitará redução de
movimento.

## 5. Dependências, execução e segurança

Não existe aplicativo executável na pasta. O vídeo não contém scripts e não requer instalação.
Ele foi decodificado como mídia, não executado como código. Não foram detectadas dependências do
modelo que possam ou devam ser incorporadas ao RarePedigree Studio.

## 6. Licença e restrições

Não há arquivo de licença. Os quadros exibem marcas **Open Pedigree X**, **PhenoTips** e aviso de
copyright. Portanto:

- nenhum logo, ícone, texto de marca ou ativo do vídeo será copiado;
- nenhum código pode ser reutilizado, pois não foi fornecido;
- a referência será usada apenas para reproduzir padrões gerais de layout e interação;
- a identidade RarePedigree/Genomic Nexus e seus SVGs próprios serão preservados.

## 7. Possibilidades de reutilização conceitual

- toolbar clara, baixa e agrupada;
- canvas dominante com controles flutuantes;
- modal com cabeçalho navy e conteúdo branco;
- search sheet sobreposto;
- formulários densos e alinhados;
- cards de escolha na abertura;
- backdrop consistente;
- legendas e controles contextuais flutuantes;
- feedback de seleção sem alterar convenções científicas.

## 8. Limitações da referência

- apenas 46,1 s de vídeo promocional;
- ausência de código, especificações, estados de hover/disabled completos e assets;
- compressão impede recuperar cores/tipografia com exatidão de fonte;
- cortes impedem medir animações com precisão;
- recursos clínicos exibidos não autorizam implementação de lógica da Fase 5;
- não há evidência de comportamento em 1366×768, HiDPI ou acessibilidade.

## 9. Comparação com o estado da Fase 4.10

| Componente atual | Referência | Diferença | Solução proposta | Prioridade |
|---|---|---|---|---|
| shell navy escuro | shell/canvas claro | contraste e densidade divergentes | tema Genomic Nexus Clinical Light extraído do vídeo | Alta |
| rail esquerda 210 px | controles flutuantes compactos | rail consome canvas | iniciar recolhida e refinar rail compacta | Alta |
| toolbar escura alta | toolbar branca baixa agrupada | hierarquia pesada | header claro, grupos e separadores | Alta |
| drawer escuro com tabs | sheet/modal branco compacto | muito espaço vazio | cards compactos, scroll e ações persistentes | Alta |
| busca navy | search sheet branca | geometria e contraste diferentes | superfície clara, header compacto e resultados densos | Alta |
| diálogos QSS genéricos | cabeçalho navy + corpo branco | acabamento inconsistente | base `NexusDialog` e decoração comum | Alta |
| menus Qt escuros | menus claros compactos | linguagem divergente | QSS claro, seleção ciano e sombra nativa | Média |
| minimapa com moldura navy | controle branco discreto | borda dominante | moldura clara e botões compactos | Média |
| abas convencionais | abas/sections discretas | densidade inadequada | tabs sublinhadas e seções compactas | Média |
| status navy | rodapé quase ausente | redundância visual | barra fina e clara | Média |

## 10. Decisão arquitetural

Foi escolhida a **Estratégia A — Qt Widgets modernizado**:

- o modelo é web, mas não há código reutilizável;
- o editor científico QGraphicsScene/QGraphicsView está validado;
- widgets customizados, QSS, `QPropertyAnimation` e overlays reproduzem os padrões observados;
- uma migração QML duplicaria o shell funcional e aumentaria risco científico;
- o protótipo `ui_next` continuará isolado.

O domínio, KinshipEngine, persistência, exportação e undo/redo não serão alterados para adequação
visual.
