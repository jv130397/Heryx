# Genomic Nexus — Design System

## Origem e escopo

Este sistema visual deriva somente de padrões observáveis no vídeo `Modelos/heredograma_linkedin.mp4`; não reutiliza código, marcas ou ativos do Open Pedigree X/PhenoTips. O editor científico, seus símbolos e suas convenções continuam independentes da decoração da interface.

## Tokens

| Papel | Token | Valor |
|---|---|---|
| Fundo de trabalho | `workspace` | `#E9ECEF` |
| Canvas | `canvas` | `#F1F3F5` |
| Superfície | `surface` | `#FFFFFF` |
| Superfície secundária | `surface_alt` | `#F7F9FA` |
| Cabeçalho modal/drawer | `header` | `#1C293B` |
| Cabeçalho hover | `header_hover` | `#26384F` |
| Ação e foco | `accent` | `#078FC2` |
| Ação hover | `accent_hover` | `#087EAA` |
| Fundo de seleção | `accent_soft` | `#E8F6FA` |
| Texto | `text` | `#1F2933` |
| Texto secundário | `muted` | `#66737F` |
| Borda | `border` | `#D6DCE1` |
| Borda forte | `border_strong` | `#B8C2CB` |

Os tokens executáveis também incluem `TYPOGRAPHY`, `ICONS`, `CONTROLS`, `ELEVATION` e `BREAKPOINTS` em `ui/theme.py`. A escala tipográfica formal é 11 px para informação auxiliar, 12 px para rótulos, 14 px para corpo, 15 px para seção, 17 px para título modal e 20 px para título de janela. Ícones usam 18/20/30 px; alvos interativos usam 44 px.

Estados semânticos usam `#238636` (sucesso), `#B7791F` (atenção) e `#C53030` (erro). Essas cores pertencem à interface; preenchimento, contorno, probando e falecimento continuam regidos pelo estilo científico.

## Geometria e tipografia

- Escala base: 14 px; títulos 16–20 px; rótulos auxiliares 11–12 px; peso 600–700 apenas para hierarquia.
- Espaçamentos: 4, 8, 12, 16, 24 e 32 px.
- Raios: 4 px para campos, 6 px para botões, 8 px para cartões e 10 px para overlays.
- Alvos interativos: mínimo de 40 px; barra compacta de 60 px; expandida de 210 px.
- Drawer: 390 px em 100%, escalável com as preferências; nunca reduz permanentemente o canvas.
- Sombras: discretas, neutras e reservadas a menus, drawers e overlays.

## Componentes

### Shell e navegação

O cabeçalho branco agrupa marca, arquivo, histórico, organização, exportação, aparência, idioma, projeto, salvamento, modo de visão e ramos. A barra lateral inicia compacta e expande sob comando, preservando área útil do heredograma.

O rail compacto tem 60 px, renderiza somente ícones centralizados e nunca usa elipse. O rail expandido tem 210 px e mostra rótulos completos. Os grupos são Edição (selecionar, mover, indivíduo, familiar, relacionamento), Organização (auto-layout, ajustar, foco) e ação destrutiva isolada no rodapé. A transição usa 160 ms `OutCubic`; redução de movimento a torna imediata.

### Canvas

Fundo cinza-claro e grade de baixo contraste. Zoom, minimapa, busca e foco são overlays; nenhum altera o modelo familiar. Símbolos clínicos mantêm cores e formas do `PedigreeRenderStyle`.

A grade usa passo de 40 unidades em zoom normal, 80 em zoom intermediário e desaparece abaixo de 30%, quando competiria com conectores. O minimapa usa moldura neutra e viewport `#078FC2`, fica fora da cena exportada e pode ser ocultado.

### Inspector

Drawer deslizante com cabeçalho azul-marinho, resumo em cartão, abas Identificação/Relações/Clínica, rolagem vertical e fechamento explícito. Relações calculadas aparecem em cartões compactos; o drawer abre apenas para seleção válida.

### Formulários e diálogos

Campos têm 36–40 px, borda neutra e foco ciano. Diálogos principais usam `NexusDialogHeader`, corpo branco e ações alinhadas. Salvar é primário; cancelar preserva os dados. Valores internos de enums não são traduzidos.

O cabeçalho modal tem 66 px e não cresce para preencher formulários curtos. Importação e exportação usam superfícies próprias com descrição, destino, formatos realmente suportados e opções existentes; o seletor nativo aparece apenas ao acionar “Procurar”. Formulários extensos devem usar rolagem, como a aba Heredograma das preferências.

### Menus, dropdowns e popovers

Superfície branca, borda de 1 px, item ativo em `accent_soft`, texto escuro e separadores discretos. Menus são `QMenu` reais; busca é um overlay independente com resultados navegáveis.

## Movimento

O drawer usa 180 ms e curva `OutCubic`. Feedback transitório dura 3,2 s. A faixa permitida é 120–220 ms; movimentos não podem bloquear entrada nem alterar a estrutura científica. A preferência de redução de movimento reduz a duração do drawer a zero.

## Internacionalização e acessibilidade

Todo texto apresentado passa por `tr()`; enums e chaves persistidas permanecem estáveis. Troca PT-BR/EN emite `languageChanged`. Controles possuem nome acessível ou tooltip, foco visível e contraste de texto compatível com superfícies claras.

## Identificadores científicos

- UUID: chave interna imutável, disponível para busca avançada e nunca usado como rótulo por padrão.
- Identificador manual: `Individual.label`, persistido e editável pelo usuário.
- Numeração genealógica: valor calculado somente para apresentação a partir da geração e ordem horizontal (`I-1`, `II-3`).

A preferência `pedigree/identifier_mode` aceita `manual`, `genealogical` e `both`. Alternar o modo recarrega somente os itens gráficos; não renomeia pessoas, UUIDs nem arquivos existentes.

## Regras de uso

1. Não usar cor decorativa para significar fenótipo.
2. Não colocar um painel fixo sobre a área do heredograma.
3. Não diminuir texto abaixo de 11 px para acomodar conteúdo.
4. Preferir rolagem e agrupamento a formulários comprimidos.
5. Não copiar marcas, ícones ou ativos do vídeo de referência.
