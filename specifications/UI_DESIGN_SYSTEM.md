# RarePedigree Scientific Workspace — Design System

## Objetivo

Este sistema visual organiza a apresentação sem alterar domínio, schema 0.2.0, layout
científico, persistência ou exportadores. A interface privilegia o canvas, ações reversíveis,
leitura clínica e operação por teclado.

## Auditoria da interface 4.5

- Toolbar combinava arquivo, edição e criação em uma faixa textual extensa.
- Toolbox duplicava comandos e consumia largura útil do canvas.
- Propriedades permaneciam como formulário desabilitado sem seleção.
- Status não informava contagem, gerações, zoom e estado de salvamento.
- Projeto vazio não orientava a primeira ação.
- Tokens visuais existiam apenas como QSS monolítico; faltavam componentes reutilizáveis.
- Grade, nomes acessíveis e validação explícita por resolução não existiam.

## Tokens

| Papel | Valor |
|---|---|
| Fundo | `#0B1220` |
| Painel | `#172338` |
| Superfície | `#1E293B` |
| Destaque | `#22D3EE` |
| Texto | `#F8FAFC` |
| Texto secundário | `#94A3B8` |
| Canvas | `#F8FAFC` |
| Borda | `#334155` |
| Perigo | `#FB7185` |

A pilha tipográfica é Inter, Noto Sans, Segoe UI e sans-serif do sistema. Controles usam
raio de 5–7 px, foco ciano de 2 px e alvos principais de pelo menos 42 px.

## Componentes

- `ToolRailButton`: ação compacta com ícone SVG, tooltip e nome acessível.
- `FamilyMenu`: expansão consistente das operações familiares existentes.
- `EmptyState`: orientação inicial funcional sobre a view, nunca na cena.
- `ZoomControl`: nível percentual, ampliar, reduzir e ajustar à tela.
- `SectionHeader`: hierarquia reutilizável para painéis.
- `PropertiesPanel`: alterna orientação e edição; relações são calculadas do projeto.
- `PedigreeView`: grade não exportável, zoom limitado e pan com botão central.

Os SVGs são próprios e definidos em `ui/icons.py`. QSS e cores ficam em `ui/theme.py`.

## Hierarquia da janela

1. Menus desktop preservados.
2. Toolbar compacta: identidade, arquivo, histórico, layout, exportação e estado.
3. Rail esquerdo: seleção, indivíduo, família, relação, layout, ajuste e exclusão.
4. Canvas central claro e dominante.
5. Propriedades redimensionáveis à direita.
6. Status: mensagem, indivíduos, gerações, salvamento e zoom.

## Interação e acessibilidade

- Atalhos: `Ctrl+N`, `Ctrl+O`, `Ctrl+S`, `Ctrl+Z`, `Ctrl+Shift+Z`, `Ctrl+L`, `Ctrl+E`,
  `Ctrl+0`, `Ctrl++`, `Ctrl+-` e `Delete`.
- Foco recebe contorno ciano, não somente alteração de cor.
- Forma, preenchimento, `?`, barra e rótulos evitam significado clínico somente por cor.
- O painel vazio não simula dados e relações calculadas não são campos editáveis.
- Exclusão pela barra solicita confirmação; undo/redo permanece disponível.

## Responsividade

O rail mantém 58 px, o painel direito é redimensionável/recolhível e o canvas recebe o espaço
restante. Testes cobrem 1366×768, 1600×900, 1920×1080 e 2560×1440. Qt fornece HiDPI e
ícones SVG evitam perda por densidade.

## Separação científica

Grade, estado vazio, rail, propriedades e status pertencem a widgets, não à `PedigreeScene`.
Os exportadores recebem somente a cena, impedindo decoração em SVG, PNG ou PDF.
