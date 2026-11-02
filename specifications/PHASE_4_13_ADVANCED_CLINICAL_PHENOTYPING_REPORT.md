# Fase 4.13 — Advanced Clinical Phenotyping & HPO Integration

## Resultado executivo

A fase implementa fenotipagem HPO estruturada, instalação oficial offline, busca indexada,
edição clínica transacional, comparação familiar, destaque temporário e exportação CSV. O motor
de parentesco, layout, cena, notas, paletas e exportadores científicos não foram reescritos.

Checkpoint anterior: `3c4b393`.

Commit principal da implementação: `36c96a4`.

## Diagnóstico inicial

- Schema `0.3.0`, sem entidade clínica estruturada.
- `Individual` possuía somente estado fenotípico geral.
- Aba Clínica mostrava um combo e aviso de indisponibilidade.
- Pacote `terminology` não tinha implementação.
- Migração preservava notas da Fase 4.12.
- Baseline: Ruff aprovado e 149 testes aprovados.
- `Modelos/`: dez PNG e um MP4, consultados sem modificação.

## Arquitetura implementada

- `domain.models`: observação HPO, estados, gravidade, evolução e lateralidade.
- `domain.phenotyping`: consultas, matriz e CSV desidentificado.
- `terminology.hpo`: OBO → SQLite FTS5, metadados e instalação oficial atômica.
- `ui.clinical`: editor da observação, painel clínico, gerenciador HPO e comparação.
- `ui.interaction`: integração na aba Clínica existente.
- `rendering.items/scene`: destaque HPO temporário, separado do preenchimento científico.
- `persistence.migrations`: schema `0.4.0`.

## Ontologia oficial validada

- Fonte: `https://purl.obolibrary.org/obo/hp.obo`.
- Versão instalada durante validação: `hp/releases/2026-09-01`.
- Termos: 20.482.
- SHA-256: `93dace952fcb3ec4728818857f6ba76bc2d5312f4d83266519b8694b8e798f22`.
- A instalação local não foi adicionada ao Git.
- Licença/proveniência: condições oficiais documentadas em
  [HPO LICENSE](https://github.com/obophenotype/human-phenotype-ontology/blob/master/LICENSE.md).

## Funcionalidades verificadas

1. Busca por ID, nome, sinônimo e correspondência parcial.
2. Definição, hierarquia, ID alternativo, obsolescência e `replaced_by`.
3. Funcionamento offline depois da indexação.
4. Instalação/atualização fora da thread principal e substituição atômica.
5. Estados presente, ausente, desconhecido e não avaliado.
6. Início, gravidade, frequência, evolução, lateralidade, fonte, data e comentários.
7. Prevenção de duplicidade por indivíduo, termo e data.
8. Histórico temporal por observações distintas.
9. Salvar/cancelar e undo/redo atômicos no editor existente.
10. Matriz familiar sem inferência de ausência.
11. Filtros por geração e ramo parental.
12. Destaque visual temporário sem mudar estado geral ou cor científica.
13. CSV explícito com opção de pseudonimização.
14. Migração sem fenótipos fictícios e preservação de notas/relações.
15. PT-BR/EN para as novas superfícies; termos permanecem no idioma oficial.

## Testes e benchmarks

```text
ruff check .
QT_QPA_PLATFORM=offscreen pytest -q
164 passed
```

Benchmarks sintéticos com 200 pessoas/200 observações e HPO completa:

| Operação | Média |
|---|---:|
| Busca HPO | 24,70 ms |
| Matriz familiar | 4,27 ms |
| Salvar projeto | 1,88 ms |
| Reabrir projeto | 12,58 ms |
| Pico Python medido | 1,31 MiB |

Dados completos: `validation/phase_4_13/performance.json`.

## Evidências visuais

Capturas de widgets Qt reais em modo offscreen, com dados clínicos sintéticos:

1. `assets/phase_4_13/01_clinical_editor_pt_1920x1080.png`
2. `assets/phase_4_13/02_hpo_autocomplete.png`
3. `assets/phase_4_13/03_clinical_editor_1366x768.png`
4. `assets/phase_4_13/04_present_observation.png`
5. `assets/phase_4_13/05_absent_observation.png`
6. `assets/phase_4_13/06_obsolete_term.png`
7. `assets/phase_4_13/07_family_comparison.png`
8. `assets/phase_4_13/08_hpo_highlight.png`
9. `assets/phase_4_13/09_hpo_preferences.png`
10. `assets/phase_4_13/10_hpo_manager.png`
11. `assets/phase_4_13/11_clinical_editor_en.png`

`validation/phase_4_13/validation.json` registra plataforma offscreen e todos os checks. Não se
afirma validação em sessão gráfica real.

## Privacidade e segurança

- Processamento clínico local e sem telemetria.
- Atualização envia apenas requisição GET ao PURL oficial.
- Download limitado, hash registrado e banco substituído somente após validação.
- CSV somente mediante ação explícita e com pseudonimização opcional.
- Mensagens e logs não incluem nomes ou conteúdo clínico.
- Não há alegação de conformidade integral com LGPD.

## Limitações

- Filtros de ramo dependem de genitores conhecidos e do gênero de representação registrado;
  estruturas ambíguas permanecem sem classificação automática.
- A pesquisa usa o inglês oficial da HPO; traduções clínicas não são inventadas.
- O gerenciador instala a versão corrente do PURL; seleção de releases históricas não está
  exposta nesta fase.
- Validação visual foi offscreen, conforme explicitamente registrado.

## Aceitação

Os requisitos centrais estão implementados e verificados com a ontologia oficial completa. Não
há transformação de manifestação isolada em diagnóstico ou estado geral afetado. A fase está
aceita tecnicamente, sujeita às limitações documentadas e a futura auditoria regulatória.
