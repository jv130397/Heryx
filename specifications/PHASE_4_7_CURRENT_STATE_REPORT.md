# RarePedigree Studio — Relatório do estado atual após a Fase 4.7

**Data da auditoria:** 2026-10-30  
**Commit auditado:** `933c1ec` (`feat: deliver phase 4.7 midnight genomics workspace`)  
**Versão declarada:** `0.2.0.dev0`  
**Schema nativo:** `0.2.0`

## 1. Conclusão executiva

O repositório está tecnicamente estável: o lint passa, os 38 testes automatizados passam e a
árvore Git estava limpa no início desta auditoria. O núcleo científico construído até a Fase
4.6 foi preservado.

Entretanto, a Fase 4.7 está **parcialmente implementada**. Há uma evolução visual real,
onboarding de idioma, preferências, cores de representação, modo monocromático, diálogos e
novos testes. Ainda assim, a implementação não satisfaz integralmente o prompt nem reproduz com
fidelidade suficiente a referência “Editor de Pedigree Genético Moderno”. O relatório anterior
`PHASE_4_7_REPORT.md` é otimista demais ao apresentar a fase como concluída.

Classificação atual:

- Núcleo científico e compatibilidade: **verificados**.
- Estabilidade automatizada: **verificada**.
- Design Midnight Genomics: **parcial**.
- Internacionalização: **parcial**.
- Preferências e personalização: **parciais**.
- Experiência avançada de edição: **parcial**.
- Critérios de aceitação da Fase 4.7: **não integralmente atendidos**.

## 2. Evidências executadas

```text
QT_QPA_PLATFORM=offscreen pytest -q
...................................... [100%]
38 passed in 0.57s

ruff check .
All checks passed!
```

Foram encontradas 11 capturas em `specifications/assets/phase_4_7/`. Elas demonstram widgets
reais, com uma ressalva: a captura do menu contextual foi composta posicionando a imagem de um
`QMenu` real sobre a captura da janela. Portanto, ela não comprova que o popup estava realmente
aberto e limitado à tela durante a captura.

## 3. Estado por requisito

| Área | Estado | Evidência e observação |
|---|---|---|
| Preservação do projeto | Concluído | Arquitetura, UUIDs, JSON, relações e schema 0.2.0 foram mantidos. |
| Checkpoint Git | Concluído | Tag `phase-4.6-checkpoint` no commit `1737046`. |
| Identidade Midnight Genomics | Parcial | Paleta e QSS existem, mas composição e acabamento ainda divergem da referência. |
| Tipografia | Parcial | Pilha Inter/Noto/Segoe definida; tamanho e escala persistidos não são aplicados globalmente. |
| Primeira inicialização | Concluído | `WelcomeDialog`, escolha PT-BR/EN e persistência por `QSettings`. |
| Internacionalização | Parcial | `QTranslator` customizado e catálogo central; não há catálogos `.ts/.qm` e todas as strings não foram centralizadas. |
| Troca de idioma sem reinício | Parcial | Superfícies principais mudam; diálogos, erros técnicos, menus contextuais e textos secundários não são todos retraduzidos. |
| Cores configuráveis | Parcial | Cores personalizadas e restauração existem; faltam paletas predefinidas e prévia integrada nas preferências. |
| Segurança cor × fenótipo | Concluído | Cor atua no contorno; afetado permanece preenchido, desconhecido conserva `?` e falecido conserva barra. |
| Modo monocromático | Concluído | Disponível na cena e na exportação, com opção independente. |
| Sexo e identidade de gênero | Pendente estrutural | `GenderIdentity` continua determinando forma gráfica; sexo atribuído ao nascimento não possui campo próprio. |
| Barra superior | Parcial | Ações e grupos existem, mas logotipo, hierarquia em duas faixas e refinamento da referência não foram reproduzidos completamente. |
| Painel esquerdo | Parcial | Ícones/rótulos e menus existem; painel não é recolhível e não há modo Mover real. |
| Canvas | Parcial | Grade, zoom, pan, fit e controle flutuante existem; faltam guias e preview de criação. |
| Editor flutuante | Parcial | Campos, cartões, prévia, cancelar e comando único existem; visual e validações ainda são básicos. |
| Abertura do editor | Concluído | Duplo clique, menu, botão e `Ctrl+I`. |
| Menu contextual | Parcial | Ações existem; compatibilidade semântica não é filtrada completamente e a captura não é uma prova de popup aberto. |
| Painel de propriedades | Parcial | Resumo, identificação e relações existem; cartões, tradução e densidade visual ainda são incompletos. |
| Assistente de projeto | Concluído funcionalmente | Metadados, representação e opção de exemplo sintético; a família sintética é gerada sem dados reais. |
| Legendas | Parcial | Mostrar/ocultar e exportar com/sem legenda funcionam; posição não é configurável. |
| Notificações | Parcial | Toast temporário existe; mensagens e níveis não cobrem de forma uniforme todos os fluxos inválidos. |
| Preferências | Parcial | Quatro abas existem; tema, fonte e escala são apresentados, mas tema e escala não têm efeito completo. |
| Responsividade | Parcialmente verificada | Testes cobrem quatro resoluções; não há teste real de escalonamento HiDPI nem auditoria assistiva. |
| Exportação | Concluído no escopo atual | SVG/PNG/PDF preservados; legenda e monocromático são independentes da interface. |
| Testes da Fase 4.7 | Parcial | Oito testes novos cobrem fluxos centrais; faltam tradução completa, popup real, HiDPI, escala aplicada e golden tests. |

## 4. O que está efetivamente implementado

### 4.1 Internacionalização

- `ui/startup.py` apresenta a seleção inicial.
- `ui/i18n.py` implementa `CatalogTranslator`, `LanguageManager` e persistência.
- Menus principais, parte da toolbar, painel de propriedades, legenda e status possuem tradução.
- A troca de idioma ocorre sem reiniciar a aplicação.

Limites verificados:

- O mecanismo é uma subclasse de `QTranslator` com dicionário Python, não um fluxo Qt completo
  com fontes `.ts` e binários `.qm`.
- Diversas strings continuam literais nos módulos de UI.
- Mensagens produzidas pelo domínio permanecem em inglês.
- Opções e diálogos abertos antes da troca podem não ser retraduzidos integralmente.

### 4.2 Aparência e componentes

- Tokens Midnight Genomics estão centralizados em `ui/theme.py`.
- Ícones SVG próprios permanecem em `ui/icons.py`.
- `ToolRailButton`, `EmptyState`, `ZoomControl`, `FamilyMenu` e `Toast` são reutilizáveis.
- Painel esquerdo expandido e propriedades à direita aproximam a estrutura da referência.

Diferenças visuais relevantes:

- Não há logotipo equivalente ao cabeçalho da referência.
- O cabeçalho não reproduz plenamente a separação entre identidade/projeto e comandos.
- Espaçamento, sombras, cartões, ícones e densidade ainda são mais simples.
- O painel esquerdo não possui a mesma organização, recolhimento ou acabamento inferior.
- O painel direito ainda usa predominantemente formulário Qt convencional.

### 4.3 Cores científicas

- `PedigreeRenderStyle` lê configurações locais.
- Homem/quadrado, mulher/círculo e não especificado/losango podem receber contornos distintos.
- As cores não substituem o estado fenotípico.
- A exportação pode forçar monocromático e restaura o estilo interativo depois.
- A legenda informa quando contornos coloridos estão ativos.

Limites:

- A nomenclatura ainda está ligada a `GenderIdentity`, o que não resolve a separação científica
  entre sexo atribuído ao nascimento, identidade de gênero e símbolo gráfico.
- Não há lista de paletas predefinidas; somente padrão, seletor personalizado e restauração.
- A tela de preferências não contém uma prévia gráfica completa.

### 4.4 Editor de indivíduo

- `EditIndividualDialog` possui identificador, cartões de forma, fenótipo, estado vital,
  proband, consultand e prévia.
- Cancelar não altera o objeto.
- Confirmar usa um único `UpdateIndividualCommand`, permitindo undo/redo.

Limites:

- A validação se restringe essencialmente ao identificador não vazio.
- Os cartões não incluem todas as opções de representação existentes no domínio.
- O diálogo ainda não alcança o acabamento visual da referência.
- Botões nativos Save/Cancel podem aparecer em inglês numa interface PT-BR.

### 4.5 Assistente e preferências

- `NewProjectDialog` coleta nome, identificador familiar, descrição, idioma, representação e
  opção sintética.
- Quando solicitado, cria uma pequena família sintética.
- `PreferencesDialog` contém Aparência, Idioma, Heredograma e Exportação.
- Cores, grade, legenda, identificadores e opções de exportação são persistidos.

Limites:

- `ui/font_size` e `ui/scale` são armazenados, mas não aplicados ao aplicativo.
- O seletor de tema possui apenas Midnight Genomics e não altera tema.
- Preferências de comportamento do layout são insuficientes.
- Não há prévia ao vivo dentro do diálogo de cores.

## 5. Testes existentes e lacunas

Os 38 testes atuais verificam regressões do domínio, migração, layout, renderização, UI 4.6 e
oito comportamentos da 4.7. A suíte é rápida e estável, mas não comprova sozinha a conclusão do
redesign.

Lacunas principais:

- inventário automatizado de strings não traduzidas;
- arquivos `.ts/.qm` e teste de cobertura de catálogo;
- aplicação real de fonte e escala;
- comportamento HiDPI;
- painel esquerdo recolhível;
- modo Mover e máquina de ferramentas;
- filtragem semântica do menu contextual;
- menu contextual realmente aberto e respeitando limites de tela;
- posicionamento da legenda;
- presets e prévia de cores;
- golden tests visuais normalizados;
- navegação completa por teclado e leitor de tela.

## 6. Compatibilidade e riscos

### Compatibilidade preservada

- Projetos 0.1.0 continuam migrando para 0.2.0.
- Campos novos do projeto possuem valores padrão.
- UUIDs existentes não são recalculados.
- JSON, SVG, PNG e PDF continuam funcionando.
- HPO, HGVS, VCF e segregação não foram introduzidos.

### Riscos atuais

- Declarar a fase concluída cria divergência entre documentação e produto.
- O uso de `GenderIdentity` como fonte da forma gráfica pode consolidar uma modelagem científica
  inadequada se não for corrigido antes de dados clínicos adicionais.
- Strings literais espalhadas tornam a internacionalização difícil de manter.
- Preferências visíveis sem efeito, como escala, prejudicam confiança do usuário.
- Testes predominantemente estruturais podem deixar regressões visuais passarem.

## 7. Avaliação dos critérios de aceitação

| Critério original | Avaliação atual |
|---|---|
| Interface próxima à referência | Parcial |
| Escolha de português ou inglês | Atendido |
| Traduções funcionais | Parcial |
| Cores configuráveis | Parcialmente atendido |
| Fenótipo distinguível das cores | Atendido |
| Janelas flutuantes | Atendido funcionalmente, parcial visualmente |
| Menus contextuais integrados | Parcial |
| Assistente de novo projeto | Atendido |
| Preferências persistentes | Atendido para os campos implementados; alguns sem efeito |
| Testes automatizados passando | Atendido |
| Projetos existentes abrindo | Atendido |
| Exportação científica correta | Atendido no escopo testado |

Resultado: **7 critérios atendidos ou funcionalmente atendidos e 5 apenas parciais**. Como o
primeiro critério e a tradução completa são centrais ao objetivo da fase, a Fase 4.7 não deve
ser considerada concluída.

## 8. Prioridades recomendadas

1. Criar matriz de rastreabilidade requisito → código → teste → captura.
2. Migrar internacionalização para `.ts/.qm` e eliminar strings literais da apresentação.
3. Aplicar efetivamente fonte e escala; testar 100%, 125%, 150% e HiDPI.
4. Reestruturar cabeçalho, rail e propriedades para se aproximarem da referência.
5. Implementar recolhimento do rail e modo Mover real.
6. Validar e filtrar ações contextuais antes de exibi-las.
7. Completar presets, prévia de cores e posição de legenda.
8. Separar representação gráfica, sexo atribuído ao nascimento e identidade de gênero no modelo,
   somente após revisão científica e plano de migração.
9. Gerar capturas reais, incluindo popup aberto, e executar comparação visual.
10. Corrigir `PHASE_4_7_REPORT.md` ou substituí-lo por um relatório final apenas após fechar as
    pendências.

## 9. Declaração final

O estado atual é um **protótipo funcional e estável da Fase 4.7**, com avanços concretos, mas
não uma implementação integral do prompt. O próximo trabalho deve ser tratado como correção da
própria Fase 4.7, e não como início da Fase 5.
