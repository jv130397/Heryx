# Catálogo de símbolos — especificação inicial

Este catálogo descreve sem reproduzir figuras protegidas. A geometria final precisa de conferência visual com as figuras originais/corrigidas antes da Fase 3.

| ID | Conceito | Renderização normativa/segura | Semântica de dados | Fonte | Estado |
|---|---|---|---|---|---|
| SYM-001 | Homem/menino | quadrado | `gender_identity=man/boy` | NSGC 2022 Fig.1 | confirmado |
| SYM-002 | Mulher/menina | círculo | `gender_identity=woman/girl` | NSGC 2022 Fig.1 | confirmado |
| SYM-003 | Gênero diverso ou não especificado | losango, com legenda/contexto | valor explícito; nunca inferir sexo | NSGC 2022 Fig.1 | confirmado |
| SYM-004 | Sexo atribuído | texto AFAB/AMAB/UAAB sob símbolo quando pertinente e autorizado | campo separado | NSGC 2022 §4.1 | confirmado |
| SYM-005 | Afetado | preenchimento/padrão definido na legenda | observação clínica vinculada a condição | NSGC 1995/2008 | confirmado |
| SYM-006 | Estado desconhecido | marcador normativo + estado explícito | `phenotype_status=unknown` | NSGC 2022 Fig.2 | confirmar geometria em QA |
| SYM-007 | Falecido | barra diagonal | vital status + data/idade/causa opcionais | NSGC 2008 Fig.1 | confirmado |
| SYM-008 | Proband/consultand | seta para o indivíduo; papéis distintos | role list | NSGC 2008 Fig.1 | confirmado |
| SYM-009 | Portador | setores/padrões com legenda; sem ponto | achado genético por condição/variante | NSGC 2022 §4.5 | confirmado |
| SYM-010 | Relação | linha horizontal | entidade `Relationship` | NSGC 1995 Fig.3 | confirmado |
| SYM-011 | Consanguinidade | linha dupla | relação biológica/coeficiente opcional | NSGC 2008 Fig.2 | confirmado |
| SYM-012 | Gêmeos | ramos de origem comum; barra entre MZ | `TwinGroup.zygosity` | NSGC 2008 Fig.2 | confirmado |
| SYM-013 | Adoção | colchetes e linha adequada | relações social e biológica separadas | NSGC 2008 Fig.2 | confirmado |
| SYM-014 | Gestação/perda/TOP/ECT/stillbirth | símbolos distintos conforme Fig.4 corrigida | `ReproductiveEvent.kind` | NSGC 2025 Fig.4 | confirmado; QA visual pendente |
| SYM-015 | Doação/gestational carrier | `D` para doador, `G` para gestational carrier e linhas tracejadas | contribuições de gameta/gestação separadas | NSGC 2025 Fig.5 | confirmado |

## Conceitos sem símbolo autônomo confirmado

Heterozigose, homozigose, hemizigose, fase cis/trans, heterozigose composta, mosaicismo, de novo, variante mitocondrial, penetrância, genótipo desconhecido, VSC/cariótipo e embrião congelado serão campos estruturados e, quando exibidos, texto/padrão explicado na legenda. O aplicativo deve rotular esses recursos como anotação técnica ou experimental, nunca “símbolo NSGC”.

