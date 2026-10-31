# RarePedigree Studio — Relatório final de validação da Fase 4.9.1

Data: 31/10/2026  
Branch auditada: `main`  
Checkpoint anterior às alterações: `dda597c`  
Checkpoint funcional intermediário: `a4045d6`

## 1. Estado inicial e resultado

A linha de base da Fase 4.9 possuía 84 testes relatados e um `KinshipEngine` funcional para parentes diretos, porém não concluía parentes indiretos, edição posterior, reconciliação, assistente em cinco etapas nem validação visual extensiva. Antes desta implementação, o repositório real foi validado com Ruff e pytest (92 testes aprovados no checkpoint local).

O estado final contém planos atômicos de parentesco direto e indireto, assistente Qt em cinco etapas com mini-heredograma real, edição de irmandade, reconciliação de desconhecidos, validação ampliada, roteamento visual por núcleos, evidências reais e artefatos persistidos/exportados. O resultado final automatizado é **110 testes aprovados e Ruff sem ocorrências**.

## 2. Arquivos principais modificados

- `src/rarepedigree/domain/kinship.py`: planos de ancestrais, descendentes, tios, primos, sobrinhos, alteração de irmandade, validação e reconciliação.
- `src/rarepedigree/ui/dialogs.py`: assistente de familiar em cinco passos, prévia real e edição de irmandade.
- `src/rarepedigree/ui/main_window.py`: ações Qt, aplicação por comando composto, undo/redo e reconciliação.
- `src/rarepedigree/rendering/scene.py`: faixas independentes para núcleos reprodutivos em ordem espacial.
- `src/rarepedigree/rendering/items.py`: conectores deslocados e rótulos de largura variável.
- `src/rarepedigree/translations/rarepedigree_en.ts/.qm`: traduções inglesas dos novos fluxos.
- `tests/unit/test_kinship_engine.py`, `test_kinship_relatives.py`, `test_relative_wizard.py`, `test_layout.py` e `test_rendering.py`.
- `scripts/validate_phase_4_9_1.py`: gerador reproduzível das evidências e do projeto final.

## 3. Matriz requisito → implementação → teste → evidência → estado

| Requisito | Implementação | Teste/evidência | Estado |
|---|---|---|---|
| Pai, mãe e genitor não especificado | planos ancestrais e assistente | suíte de parentesco; capturas 01/02 | Completo |
| Avós e bisavós antes dos genitores | caminho ancestral cria/reutiliza intermediários autorizados | `test_kinship_relatives.py` | Completo |
| Filhos, netos e bisnetos | `plan_descendant` atômico | teste de bisneto | Completo |
| Tios maternos/paternos e meio-tios | `plan_aunt_uncle`, ramo e tipo de irmandade explícitos | testes materno e meio-tio paterno; captura 07 | Completo no domínio |
| Primos antes dos tios | plano cria/reutiliza ramo intermediário | teste de ordem; captura 07 | Completo |
| Sobrinhos antes dos irmãos | plano cria/reutiliza irmão intermediário | teste específico | Completo |
| Irmãos completos, meios-irmãos e não resolvidos | `plan_sibling` e seleção do outro genitor | testes do motor/assistente; capturas 03/04 | Completo |
| Irmandade adotiva/social | vínculo declarado sem inventar parentalidade biológica | testes do motor | Completo no domínio |
| Não inferir casamento | coparentalidade permanece em `Parentage`; `Relationship` não é criado | testes de layout; demo tem 0 relacionamentos afetivos inventados | Completo |
| Assistente em cinco etapas | cinco `QWizardPage`; plano isolado; `PedigreeScene` real | 3 testes Qt; capturas 09/10 | Completo |
| Cancelamento sem mutação | cópia profunda e aplicação somente após confirmação | teste Qt | Completo |
| Edição de irmandade | diálogo e `plan_change_sibling_kind` | testes de conversão | Completo |
| Reconciliação de desconhecido | substituição de UUID nas arestas e deduplicação | testes de reconciliação | Completo |
| Corrigir ramo errado de tio/primo | motor permite reconstrução, mas não há assistente dedicado de migração de ramo | inspeção de UI | **Parcial** |
| Validador científico | ciclos, referências, duplicações, contradições e ambiguidades | testes do validador | Completo para regras implementadas |
| Layout por gerações/núcleos | sweep baricêntrico, unidades familiares e faixas reprodutivas ordenadas espacialmente | testes 50/100/200; capturas 01–08/11 | Completo com limitação de densidade |
| Rótulos legíveis e gerações à esquerda | bounds dinâmico e coluna romana comum | teste de bounds; capturas | Completo |
| PT-BR/EN | novas strings adicionadas ao `.ts` e `.qm` | compilação `pyside6-lrelease` | Completo para o fluxo novo |
| Compatibilidade JSON/exportações | modelo existente preservado; save/reopen; SVG/PNG/PDF | artefatos em `validation/phase_4_9_1` | Completo |
| QML Genomic Nexus | nenhuma ponte QML funcional foi encontrada como requisito ativo do editor Qt Widgets | auditoria do repositório | Não aplicável nesta entrega |

## 4. Correções científicas e estruturais

- Uma criança criada a partir de um único genitor recebe um coparente estrutural desconhecido sem inferir casamento ou parceria.
- Meio-irmãos paternos e maternos usam núcleos parentais distintos e preservam a identidade conhecida do genitor compartilhado.
- Parentes indiretos são produzidos por um `KinshipPlan` único; intermediários existentes são reutilizados e desconhecidos só são criados quando autorizados.
- A reconciliação reescreve arestas de parentalidade, relações declaradas e grupos de gêmeos, removendo duplicações após a substituição.
- O layout não usa proximidade como verdade: todas as conexões são derivadas das arestas do domínio.

## 5. Testes executados

```text
conda run -n rarepedigree-studio ruff check .
All checks passed!

QT_QPA_PLATFORM=offscreen conda run -n rarepedigree-studio pytest -q
110 passed in 3.55s
```

Os testes novos verificam o grafo, incluindo pais reais de cada novo indivíduo, distinção de meio-irmãos, reutilização de intermediários, deduplicação, cancelamento e gerações exatas. Famílias sintéticas de 50, 100 e 200 indivíduos têm posições únicas e toda aresta pai→filho avança exatamente uma geração.

## 6. Evidências visuais reais

As imagens foram obtidas com `QWidget.grab()` da aplicação/assistente reais; não são montagens:

1. [Três gerações](assets/phase_4_9_1/01_three_generations.png)
2. [Quatro gerações](assets/phase_4_9_1/02_four_generations.png)
3. [Meio-irmãos paternos](assets/phase_4_9_1/03_paternal_half_siblings.png)
4. [Meio-irmãos maternos](assets/phase_4_9_1/04_maternal_half_siblings.png)
5. [Pai e três mães](assets/phase_4_9_1/05_father_three_mothers.png)
6. [Mãe e três pais](assets/phase_4_9_1/06_mother_three_fathers.png)
7. [Tios e primos](assets/phase_4_9_1/07_aunts_cousins.png)
8. [Indivíduos desconhecidos](assets/phase_4_9_1/08_unknown_people.png)
9. [Assistente](assets/phase_4_9_1/09_relative_wizard.png)
10. [Prévia real](assets/phase_4_9_1/10_wizard_preview.png)
11. [Família com 50 indivíduos](assets/phase_4_9_1/11_large_family_50.png)

A inspeção manual encontrou e corrigiu linhas reprodutivas coincidentes, ordem de faixas dependente de UUID e rótulos longos cortados. Núcleos independentes agora usam faixas distintas ordenadas da esquerda para a direita.

## 7. Cenário final, persistência e exportação

O cenário é construído em ordem não genealógica e contém probando, pais, quatro avós, dois irmãos completos, meio-irmão paterno, meia-irmã materna, tio paterno, tia materna estrutural, dois primos, sobrinho e desconhecido reconciliado. Resultado reaberto: 21 indivíduos, 24 arestas de parentalidade e nenhuma parceria conjugal inventada.

Artefatos:

- `validation/phase_4_9_1/phase_4_9_1_demo.rps.json`
- `validation/phase_4_9_1/phase_4_9_1_demo.svg`
- `validation/phase_4_9_1/phase_4_9_1_demo.png`
- `validation/phase_4_9_1/phase_4_9_1_demo.pdf`
- `validation/phase_4_9_1/validation.json`

## 8. Limitações restantes

1. A correção posterior de um tio/primo colocado no ramo errado ainda exige desfazer/recriar ou manipulação pelo motor; falta um assistente específico que mostre consequências e migre o ramo.
2. Pedigrees excepcionalmente densos podem manter cruzamentos inevitáveis e exigem zoom ou ajuste manual. O algoritmo reduz cruzamentos, mas não promete planaridade para grafos não planares ou múltiplos núcleos sobrepostos.
3. A captura de 50 indivíduos comprova o comportamento do editor, mas a legibilidade de identificadores em uma única tela depende da resolução; zoom/pan permanecem necessários.
4. Não foi encontrada uma interface QML funcional equivalente que justificasse duplicar a integração; o fluxo validado é o editor Qt Widgets principal.

## 9. Decisão de aceitação

A Fase 4.9.1 está **funcionalmente aceita para criação, edição de irmandade, reconciliação, persistência e exportação**, com cobertura automatizada superior à linha de base. Ela **não é declarada integralmente encerrada** porque o assistente dedicado para migrar tios/primos entre ramos ainda está ausente e porque famílias extremamente densas conservam uma limitação visual documentada. Esses pontos não corrompem o grafo, mas devem ser tratados antes de afirmar atendimento literal de todos os critérios da especificação.
