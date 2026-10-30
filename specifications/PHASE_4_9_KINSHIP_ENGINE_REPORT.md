# RarePedigree Studio — Relatório técnico da Fase 4.9

## Estado da entrega

Este documento registra o estado real após a primeira implementação do motor de parentesco da
Fase 4.9. A fase permanece **em andamento**: os requisitos centrais de irmandade e múltiplos
núcleos parentais estão implementados e testados, mas a expansão assistida de parentes colaterais,
a edição posterior completa e toda a matriz visual ainda não estão concluídas. Esses itens não são
apresentados como funcionais.

Checkpoint anterior às mudanças: `a2405ad` (`chore: checkpoint before phase 4.9 kinship engine`).
Baseline: Ruff aprovado e 67 testes aprovados.

## Diagnóstico inicial

- `FamilyService.add_sibling` sempre copiava todos os genitores e, portanto, só representava
  irmãos completos.
- Não existiam parentescos declarados para irmandade não esclarecida, adotiva ou social.
- `placeholder` distinguia parcialmente desconhecidos, mas não armazenava motivo nem
  proveniência.
- O domínio já separava `Parentage` de `Relationship`, porém `add_parents` criava uma parceria
  automaticamente. O novo motor não faz essa inferência.
- O layout agrupava apenas parceiros registrados. Coparentes sem relacionamento explícito podiam
  ficar visualmente distantes.
- A validação Pydantic já detectava referências ausentes e ciclos, mas não duplicidade nem mais de
  dois genitores biológicos.
- A substituição integral do projeto por `ReplaceProjectCommand` já fornecia a base correta para
  undo/redo atômico.

## Arquitetura implementada

`domain/kinship.py` é independente de Qt e contém:

- `KinshipEngine`: consultas, inferência de irmãos, planejamento e reconciliação;
- `KinshipPlan`: prévia imutável em relação ao projeto de origem e aplicação atômica;
- `KinshipValidator`: validações semânticas adicionais;
- `SiblingKind`: irmão completo, meio-irmão paterno, meio-irmão materno, não esclarecido,
  adotivo e social;
- `KinshipIssue` e `KinshipSeverity`: resultado estruturado para erro, ambiguidade e aviso.

O modelo recebeu campos opcionais compatíveis com documentos 0.2.0:

- `Individual.unknown_reason` e `Individual.provenance`;
- `Parentage.evidence_status` e `Parentage.provenance`;
- `DeclaredKinship`, com tipo, evidência e proveniência;
- `PedigreeProject.declared_kinships` com default vazio.

Não houve migração destrutiva nem alteração dos UUIDs. Arquivos antigos continuam válidos porque
os novos campos possuem defaults. O versionamento do schema permanece 0.2.0 nesta etapa; uma
elevação só deverá ocorrer quando o conjunto de novos campos estiver estabilizado.

## Matriz de parentescos e rastreabilidade

| Parentesco/requisito | Implementação | Teste/evidência | Estado |
|---|---|---|---|
| Irmãos completos | reutiliza dois genitores; cria representantes provisórios se autorizados | `test_full_sibling_*` | Completo no domínio e acessível na UI |
| Meio-irmãos paternos | compartilha apenas pai; mãe existente ou desconhecida diferente | `test_paternal_half_*` | Completo no domínio; UI cria a mãe desconhecida |
| Meio-irmãos maternos | compartilha apenas mãe; pai existente ou desconhecido diferente | `test_maternal_half_*` | Completo no domínio; UI cria o pai desconhecido |
| Irmandade não esclarecida | `DeclaredKinship`; não cria parentalidade | `test_declared_siblings_*` | Completo |
| Irmãos adotivos e sociais | declaração separada da ancestralidade genética | `test_declared_siblings_*`, `test_non_biological_*` | Completo no domínio |
| Gêmeos | serviço preexistente, preservado | suíte anterior | Existente; não integrado ao novo assistente |
| Pai com 2/3 mães e mãe com 2/3 pais | núcleos independentes por arestas de parentalidade | testes de layout e famílias de 50/100/200 | Completo no domínio/layout básico |
| Não inferir casamento por filho compartilhado | motor não cria `Relationship` | `test_full_sibling_*`, `test_coparents_*` | Completo |
| Ascendentes e descendentes | busca por distância mínima | `test_ancestors_and_descendants_*` | Consulta completa; criação assistida pendente |
| Avós/bisavós em qualquer ordem | — | — | Não implementado no novo motor |
| Tios, primos e sobrinhos | — | — | Não implementado |
| Desconhecido com proveniência | placeholder, motivo, proveniência e UUID estável | testes de meio-irmão e persistência | Parcial: criação/reconciliação disponíveis |
| Reconciliação | substituição planejada e validada por indivíduo existente | `test_unknown_reconciliation_*` | Completo para reconciliação simples |
| Ciclo ancestral | validação preexistente preservada | suíte anterior | Completo |
| Parentalidade duplicada | `KinshipValidator` | `test_validator_reports_*` | Completo |
| Mais de dois genitores biológicos | `KinshipValidator` | `test_validator_reports_*` | Completo |
| Operação atômica/undo | `KinshipPlan` + `ReplaceProjectCommand` | testes do motor e suíte da janela | Completo para fluxo integrado |
| Persistência de parentesco declarado | JSON nativo | `test_repository_preserves_declared_kinship` | Completo |
| Edição posterior do tipo de irmão | — | — | Não implementado |
| Assistente em cinco etapas | diálogo com identificação, tipo e prévia textual | testes de domínio; inspeção de código | Parcial |
| QML/Genomic Nexus | nenhuma lógica científica duplicada | arquitetura | Não integrado |

## Regras científicas efetivamente aplicadas

1. Parentesco biológico é inferido exclusivamente de `ParentageKind.BIOLOGICAL`.
2. Parentalidade social ou legal não alimenta inferência genética.
3. Dois genitores compartilhados classificam irmãos completos.
4. Um pai compartilhado classifica meio-irmãos paternos; uma mãe compartilhada classifica
   meio-irmãos maternos.
5. Genitor com representação não especificada produz irmandade não resolvida, não uma conclusão
   paterna ou materna.
6. Ausência de identificação não equivale a identidade: o genitor diferente recebe UUID próprio,
   `placeholder=True`, motivo e proveniência.
7. Coparentalidade não cria parceria, casamento ou coabitação.
8. Planejamento não modifica o projeto de origem; falhas impedem a aplicação integral.

## Organização automática

O layout usa gerações derivadas do grafo. Componentes horizontais agora consideram tanto
parcerias explícitas quanto coparentalidade. A coparentalidade é somente uma restrição de layout e
não é persistida como `Relationship`. Filhos de genitores diferentes mantêm conectores separados.

Verificações automatizadas cobrem ausência de colisão em núcleos múltiplos e famílias sintéticas
de 50, 100 e 200 indivíduos. Isso não equivale ainda a comprovar minimização ótima de cruzamentos
ou legibilidade clínica em todos os casos.

## Interface

O comando **Adicionar irmão** abre, quando a janela está visível, um diálogo que exige uma das
seis classificações, aceita identificador e apresenta uma prévia das consequências. Cancelar sai
antes de criar o plano. O projeto só é substituído depois da validação, como um comando único de
undo/redo.

Limitações atuais do diálogo:

- ainda não permite escolher visualmente um “outro genitor” existente;
- ainda não é um wizard completo em cinco páginas;
- a prévia é textual, sem mini-heredograma;
- strings novas ainda precisam entrar no catálogo `.ts/.qm` em inglês.

## Arquivos modificados

- `src/rarepedigree/domain/models.py`
- `src/rarepedigree/domain/kinship.py` (novo)
- `src/rarepedigree/domain/family_service.py`
- `src/rarepedigree/domain/__init__.py`
- `src/rarepedigree/layout/engine.py`
- `src/rarepedigree/ui/dialogs.py`
- `src/rarepedigree/ui/main_window.py`
- `tests/unit/test_kinship_engine.py` (novo)
- `tests/unit/test_layout.py`
- `tests/unit/test_json_repository.py`

## Testes executados

```text
conda run -n rarepedigree-studio ruff check .
All checks passed!

QT_QPA_PLATFORM=offscreen conda run -n rarepedigree-studio pytest -q
84 passed
```

O ambiente Conda existente `rarepedigree-studio` foi reutilizado; não foi necessário criar outro.

## Validação visual

As capturas obrigatórias da Fase 4.9 ainda não foram produzidas nesta etapa. Portanto, não há
alegação de aprovação visual para famílias de 3/4 gerações, meios-irmãos, três núcleos parentais,
tios/primos ou 50 indivíduos. Os testes offscreen verificam estrutura, gerações e colisão de
coordenadas, mas não substituem inspeção visual humana.

## Pendências priorizadas

1. Completar o assistente com seleção/criação explícita dos genitores e prévia gráfica.
2. Implementar planejadores de avós, bisavós, tios, primos e sobrinhos com resolução de
   ambiguidades.
3. Implementar mudança posterior do tipo de relação com análise de impacto em terceiros.
4. Expandir o validador para contradições entre declarações, irmandade e parentagens.
5. Tratar reconciliação com deduplicação segura de arestas e histórico explícito.
6. Melhorar ordenação do layout para reduzir cruzamentos em famílias extensas/consanguíneas.
7. Integrar o mesmo serviço ao protótipo QML, sem portar regras para QML.
8. Completar traduções PT-BR/EN.
9. Executar toda a matriz de exportação e capturas reais.

## Resultado de aceitação

A entrega atual comprova os critérios centrais 2, 3, 4, 5, 6, 10, 11 e 13 da especificação para
os fluxos implementados. Os critérios 1, 7, 8, 9, 12, 14 e 15 ainda exigem as pendências acima.
Consequentemente, a Fase 4.9 **não deve ser declarada concluída** neste checkpoint.
