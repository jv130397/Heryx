# RarePedigree Studio — Fase 4.9.2

## Scientific Pedigree Layout & Relationship Refinement

Data: 31/10/2026  
Checkpoint inicial: `851db41`  
Linha de base confirmada: Ruff limpo e 110 testes aprovados.

## 1. Diagnóstico científico e visual

A auditoria comparou o projeto armazenado, as arestas renderizadas e as capturas da Fase 4.9.1. Nenhum cenário auditado possuía parentalidade armazenada diferente daquela pretendida. Os defeitos encontrados eram de roteamento ou apresentação.

| Cenário | Origem/destino | Relação e núcleo | Convenção | Diagnóstico inicial | Classificação |
|---|---|---|---|---|---|
| 3 e 4 gerações | par parental → sibship | parentalidade biológica | união horizontal, linha de descendência e barra de irmãos | estrutura e rotas coerentes | correto |
| Meio-irmãos paternos | pai compartilhado + mães distintas → filhos | núcleos biológicos distintos | uma união por par parental | genitores corretos; faixas próximas | estética/roteamento |
| Meio-irmãos maternos | mãe compartilhada + pais distintos → filhos | núcleos biológicos distintos | uma união por par parental | genitores corretos; faixas próximas | estética/roteamento |
| Pai, três mães | pai compartilhado + C1/C2/C3 → F1/F2/F3 | três núcleos independentes | três uniões reprodutivas | linha do núcleo distante atravessava símbolos intermediários | **erro de roteamento** |
| Mãe, três pais | mãe compartilhada + C1/C2/C3 → F1/F2/F3 | três núcleos independentes | três uniões reprodutivas | problema simétrico ao anterior | **erro de roteamento** |
| Tios e primos | avós → genitor/tio; tio + coparente → primo | sibship e descendência | barras ortogonais | cruzamentos evitáveis por ordem de faixa | **erro de roteamento** |
| Desconhecidos | representante provisório → descendente | parentalidade provisória | linha tracejada apenas quando a aresta não é biológica | conceitos visuais pouco diferenciados | problema semântico/estético |
| Família de 50 | vários núcleos em quatro gerações | parentalidades biológicas | barras por núcleo | comprimentos grandes e faixas coincidentes | roteamento/densidade |

O tracejado não foi usado como solução de colisão. Ele permanece reservado a símbolos provisórios e a parentalidade cujo `ParentageKind` não é biológico.

## 2. Correções dos conectores

- Cada `ParentageConnectorItem` expõe os segmentos ortogonais que efetivamente desenha.
- Âncoras partem das bordas dos símbolos e chegam ao topo dos descendentes.
- Núcleos com um genitor compartilhado recebem faixas abaixo dos identificadores: 68 px, 82 px, 96 px e seguintes.
- Núcleos independentes permanecem na faixa natural; não recebem deslocamento baseado em UUID.
- A barra de irmãos é limitada por uma margem antes dos símbolos.
- O roteador mede interseções com símbolos, cruzamentos entre conectores, colisões, comprimento total e comprimento máximo.
- A linha selecionada recebe destaque ciano e uma área de clique ampliada, sem alterar o estilo científico exportado.

O defeito crítico “linha atravessando outro parceiro” passou de quatro interseções detectadas para zero nos dois cenários de múltiplos parceiros.

## 3. Símbolos desconhecidos

Os conceitos agora são representados separadamente:

| Conceito | Representação |
|---|---|
| Sexo/gênero não especificado | losango |
| Fenótipo não conhecido | interrogação dentro do símbolo |
| Representante estrutural provisório | borda tracejada e rótulo auxiliar “representante provisório” |
| Pessoa real não identificada | símbolo correspondente aos dados conhecidos, sem receber automaticamente o estado `placeholder` |
| Parentesco não esclarecido | `DeclaredKinship`, sem inventar aresta biológica |

O rótulo auxiliar pode ser ocultado pela preferência `pedigree/show_auxiliary_labels`; os dados e a proveniência permanecem no projeto.

## 4. Métricas finais

Resultados reproduzíveis de `validation/phase_4_9_2/validation.json`:

| Cenário | Colisões | Linha × símbolo | Cruzamentos | Sobreposições | Comprimento total | Maior conector |
|---|---:|---:|---:|---:|---:|---:|
| Quatro gerações | 0 | 0 | 0 | 0 | 2410 | 698 |
| Pai, três mães | 0 | 0 | 0 | 0 | 1725 | 814 |
| Mãe, três pais | 0 | 0 | 0 | 0 | 1725 | 786 |
| Tios e primos | 0 | 0 | 0 | 0 | 1678 | 536 |
| Família de 50 | 0 | 0 | 0 | 0 | 13111,67 | 3704,67 |
| Migração — antes | 0 | 0 | 0 | 0 | 1142 | 536 |
| Migração — depois | 0 | 0 | 0 | 0 | 1490 | 536 |

As métricas não prometem planaridade universal. Elas contam cruzamentos próprios entre segmentos de conectores sem um indivíduo compartilhado, sobreposições colineares e interseções com símbolos que não são endpoints daquele núcleo.

## 5. Migração de ramos familiares

Foi implementado `KinshipEngine.plan_reassign_collateral_branch` e o `ReassignBranchWizard`.

O fluxo:

1. identifica se o selecionado é tio/tia ou primo/prima do probando;
2. mostra ramo e intermediário atuais;
3. permite escolher ramo paterno ou materno e tipo de irmandade do intermediário;
4. lista parentalidades substituídas e descendentes preservados;
5. produz uma prévia com `PedigreeScene` real;
6. exige confirmação;
7. aplica um único `ReplaceProjectCommand`;
8. suporta undo/redo.

Somente as parentalidades biológicas de entrada do intermediário colateral são substituídas. Filhos, coparentes e demais relações de terceiros não são apagados silenciosamente. Se o ramo de destino não possuir ascendentes suficientes, representantes provisórios são criados, exibidos na prévia e registrados com proveniência.

## 6. Inspeção contextual

O painel deslizante passou a apresentar:

- identificador e estado do indivíduo;
- parentesco calculado com o probando;
- genitores conhecidos e representantes provisórios;
- irmãos completos e meio-irmãos;
- parceiros cadastrados e descendentes;
- erros ou ambiguidades associados ao indivíduo.

Conectores de parentalidade são selecionáveis. O inspetor mostra genitores, descendentes, UUIDs, `ParentageKind` e `EvidenceStatus` de todas as arestas representadas pelo conector.

## 7. Comparação visual

Referência anterior: `specifications/assets/phase_4_9_1/`.

Capturas autênticas posteriores:

- [Quatro gerações](assets/phase_4_9_2/after_four_generations.png)
- [Pai com três mães](assets/phase_4_9_2/after_father_three_mothers.png)
- [Mãe com três pais](assets/phase_4_9_2/after_mother_three_fathers.png)
- [Tios e primos](assets/phase_4_9_2/after_aunts_cousins.png)
- [Família de 50 indivíduos](assets/phase_4_9_2/after_extended_50.png)
- [Ramo antes da migração](assets/phase_4_9_2/branch_before.png)
- [Ramo depois da migração](assets/phase_4_9_2/branch_after.png)
- [Assistente e prévia de impacto](assets/phase_4_9_2/branch_migration_preview.png)

As imagens foram produzidas por `QWidget.grab()` da aplicação real, com os mesmos dados usados nas métricas.

## 8. Testes e artefatos

Foram adicionados testes para:

- segmentos e identificação do núcleo parental;
- conectores selecionáveis;
- núcleos independentes e múltiplos coparentes;
- ausência de linha atravessando símbolos;
- métricas de layout;
- migração de tia e primo entre ramos;
- preservação de descendentes e terceiros;
- prévia sem mutação do projeto;
- undo/redo em uma operação;
- inspeção contextual de conexão;
- famílias de 50, 100 e 200 indivíduos já preservadas da fase anterior.

Validação final:

```text
conda run -n rarepedigree-studio ruff check .
All checks passed!

QT_QPA_PLATFORM=offscreen conda run -n rarepedigree-studio pytest -q
117 passed in 3.47s
```

A auditoria serializada contém todos os núcleos parentais e confirmou zero itens com conflitos geométricos nos cenários finais.

Persistência e exportações reais:

- `validation/phase_4_9_2/branch_migration_demo.rps.json`
- `validation/phase_4_9_2/branch_migration_demo.svg`
- `validation/phase_4_9_2/branch_migration_demo.png`
- `validation/phase_4_9_2/branch_migration_demo.pdf`
- `validation/phase_4_9_2/validation.json`

## 9. Limitações restantes

- Em uma árvore larga, o maior conector pode ser longo; zoom e pan continuam necessários para leitura confortável.
- As métricas tratam cruzamentos geométricos, não substituem revisão clínica do significado das arestas.
- Relações colaterais não redutíveis a parentalidade confirmada continuam explicitamente “não esclarecidas”; o programa não fabrica um ramo para melhorar a aparência.
- Consanguinidade, gêmeos e adoção continuam preservados pelos itens especializados existentes; esta fase não alterou suas convenções.

## 10. Decisão de aceitação

A Fase 4.9.2 é aceita para os cenários definidos. Não há, nas evidências finais, linha de parentalidade atravessando símbolo, colisão de símbolos ou cruzamento evitável detectado. A migração de tios/primos entre ramos está disponível, é pré-visualizada, atômica e reversível. As limitações restantes afetam escala de visualização, não induzem parentalidade diferente daquela armazenada.
