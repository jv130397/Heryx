# Auditoria de redundâncias da interface após a Fase 4.11

## Escopo

Auditoria estática dos fluxos realmente conectados em `MainWindow`, menus, toolbar, rail, canvas, editor flutuante, painel de propriedades, preferências e protótipo QML. Nenhuma função foi removida nesta etapa. A pasta `Modelos/` permaneceu intocada.

## Resumo executivo

Há redundância útil em alguns comandos globais: menu, toolbar e atalho para salvar ou desfazer são padrões desktop e devem permanecer. A redundância problemática concentra-se nas ações dependentes de um indivíduo selecionado. Atualmente a mesma intenção pode ser apresentada no rail, no menu Heredograma, no menu de clique direito e na barra contextual.

As maiores fontes de confusão são:

1. `PropertiesPanel` continua contendo um formulário completo de indivíduo, embora a seleção comum use `FloatingIndividualEditor`.
2. “Abrir propriedades” ainda reativa o drawer que o fluxo aprovado substituiu.
3. Adicionar pais, parceiro, filho ou irmão aparece em quatro lugares.
4. Rótulos podem ser configurados tanto em Preferências quanto em um diálogo dedicado.
5. A árvore `ui_next/` mantém uma segunda interface QML independente, sem ser o entrypoint principal.

## Matriz de redundâncias

| Função | Onde aparece | Classificação | Recomendação | Prioridade |
|---|---|---|---|---|
| Novo, abrir, salvar | Menu Arquivo e toolbar; também atalhos | Redundância legítima | Manter | — |
| Undo/redo | Menu Editar, toolbar e atalhos | Redundância legítima | Manter | — |
| Exportar | Menu Arquivo, toolbar e atalho | Redundância legítima | Manter | — |
| Preferências | Menu Arquivo e toolbar | Aceitável, porém toolbar carregada | Manter no menu; avaliar retirar da toolbar após teste de uso | Baixa |
| Adicionar indivíduo básico | Menu Heredograma e rail “Adicionar indivíduo” | Redundância acessível | Manter rail como principal e menu como alternativa acessível | Baixa |
| Adicionar pais/parceiro/filho/irmão | Menu Heredograma, rail “Adicionar familiar”, clique direito e barra contextual | Redundância excessiva | Barra contextual como fluxo primário; rail apenas “Adicionar familiar…” avançado; menu desktop como fallback; retirar ações básicas do clique direito | Alta |
| Editar indivíduo | Atalho/menu, duplo clique, clique direito, barra contextual, botão do painel legado | Redundância excessiva | Todos os gatilhos podem continuar, mas devem abrir exclusivamente o mesmo `FloatingIndividualEditor`; remover o botão duplicado do painel | Alta |
| Propriedades do indivíduo | `PropertiesPanel`/drawer e `FloatingIndividualEditor` | Dois editores concorrentes | Converter drawer em inspector somente leitura de relações/conectores ou removê-lo da edição individual | Crítica |
| “Abrir propriedades” | Clique direito | Contradiz o fluxo aprovado | Remover para indivíduos; manter inspector apenas ao selecionar uma conexão | Crítica |
| Estado fenotípico | Formulário do drawer e aba Clínica flutuante | Campo duplicado | Editar somente no editor flutuante | Alta |
| ID, gênero, falecido, proband, consultand | Drawer e editor flutuante | Campos duplicados | Editar somente no editor flutuante | Alta |
| Relações calculadas e avisos | Drawer | Informação única e útil | Preservar como inspector somente leitura, acessível por comando explícito se necessário | Média |
| Inspeção de conector parental | Drawer | Função única | Preservar até existir inspector contextual próprio de conexão | Alta |
| Configurar rótulos | Menu Exibir/dialog dedicado e Preferências › Heredograma | Mesma configuração em dois formulários | Manter uma única implementação; ação “Configurar rótulos…” deve abrir diretamente a aba Heredograma de Preferências ou o diálogo dedicado deve substituir os campos de Preferências | Alta |
| Organização automática | Menu Exibir, toolbar e rail | Três acessos globais | Retirar da toolbar ou rail; recomendação: manter rail e menu/atalho | Média |
| Ajustar à tela | Menu Exibir, rail, menu do canvas e atalho | Redundância aceitável para navegação | Manter menu do canvas, rail e atalho; menu Exibir é fallback | Baixa |
| Excluir | Menu Heredograma, rail, clique direito e tecla Delete | Redundância aceitável, mas arriscada | Manter tecla/menu contextual com confirmação; retirar botão permanente inferior do rail se exclusão acidental for observada | Média |
| Relacionar selecionados | Menu Heredograma e rail | Redundância funcional | Manter rail como principal e menu acessível | Baixa |
| Focar probando | Menu Exibir, rail, toolbar “Ramos” e atalho | Funções parcialmente sobrepostas | Centralizar navegação de ramos no controle “Ramos”; manter atalho, retirar botão dedicado do rail | Média |
| `ui/` versus `ui_next/` | Widgets principal e protótipo QML independente | Duas implementações de interface | Declarar `ui_next` experimental ou arquivar; não evoluir ambas em paralelo | Alta técnica |

## Evidências no código

- O entrypoint `src/rarepedigree/__main__.py` instancia `ui.MainWindow`; `ui_next` só possui entrypoint independente.
- `PropertiesPanel` contém ID, gênero, fenótipo, estado vital, proband, consultand e posição, campos também expostos no editor flutuante.
- `IndividualItem.build_context_menu()` ainda oferece criação de familiares, edição e “Abrir propriedades”.
- `_create_toolbox()` e `_create_menus()` reutilizam as mesmas ações familiares, enquanto `ContextualFamilyBar` oferece novamente essas ações.
- `PreferencesDialog._pedigree_tab()` e `LabelConfigurationDialog` gravam as mesmas chaves `pedigree/identifier_mode` e `pedigree/show_auxiliary_labels`.
- `properties_dock` é apenas um alias legado para `properties_drawer` e não possui uso interno adicional.

## Plano de consolidação sem reescrever módulos funcionais

### Etapa 1 — baixo risco

1. Remover “Abrir propriedades” do menu de indivíduo.
2. Fazer menu, atalho, duplo clique e barra contextual abrirem o mesmo editor flutuante.
3. Retirar do clique direito as ações familiares básicas já apresentadas visualmente pela barra contextual.
4. Manter no clique direito apenas editar, focar, centralizar, excluir e operações avançadas não presentes na barra.

### Etapa 2 — preservar inspeção científica

1. Tornar `PropertiesPanel` somente leitura.
2. Preservar relações calculadas, avisos e inspeção de conectores.
3. Remover do painel os campos editáveis e o botão “Editar indivíduo”.
4. Renomear o drawer para “Inspector de relações” e abri-lo somente sob solicitação explícita ou seleção de conexão.

### Etapa 3 — simplificar navegação

1. No rail, substituir a lista de pais/parceiro/filho/irmão por uma única ação “Adicionar familiar…”.
2. Preservar opções avançadas — adoção, desconhecidos, correção de ramo e reconciliação — no assistente.
3. Concentrar foco de ramos no controle superior “Ramos”.
4. Manter menus desktop para acessibilidade e atalhos, sem tratá-los como fluxo visual principal.

### Etapa 4 — dívida arquitetural

1. Marcar `ui_next` explicitamente como protótipo experimental ou arquivá-lo após confirmar que não é distribuído.
2. Evitar implementar novas funcionalidades nas duas interfaces.
3. Remover o alias `properties_dock` após confirmar ausência de integração externa.

## Testes necessários antes da remoção

- Todos os gatilhos de edição abrem uma única instância do editor flutuante.
- Selecionar indivíduo nunca abre o drawer.
- Selecionar conector continua mostrando genitores, descendentes e evidência.
- Ações familiares continuam disponíveis por barra contextual e por um caminho acessível de teclado.
- Cancelamento não altera o projeto; confirmação continua undoable.
- Configuração de rótulos possui uma única fonte de verdade.
- Projetos antigos, exportação e os testes do motor de parentesco permanecem inalterados.

## Decisão recomendada

Executar primeiro as Etapas 1 e 2. Elas removem a contradição visual mais evidente sem tocar no motor de parentesco, no modelo persistente ou no layout científico. A Etapa 3 deve vir depois de uma captura real e teste de acessibilidade. `ui_next` deve ser tratado separadamente como decisão arquitetural, não apagado junto com componentes visuais.
