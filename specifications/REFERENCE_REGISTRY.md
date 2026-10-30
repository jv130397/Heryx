# Registro de referências

Consulta em **2026-10-30**. O nível “primária” significa editor, organização mantenedora, PubMed/PMC ou repositório oficial.

| Ref. | Referência e identificador | Versão/data verificada | Acesso/arquivo | Uso e estado |
|---|---|---|---|---|
| REF-NSGC-1995 | Bennett et al. DOI 10.1007/BF01408073 | 1995 | PDF local | Base, confirmada; parcialmente superada. |
| REF-NSGC-2008 | Bennett et al. DOI 10.1007/s10897-008-9169-9; PMID 18792771 | 2008 | PDF local | Atualização, confirmada. |
| REF-NSGC-2022 | Bennett et al. DOI 10.1002/jgc4.1621; PMID 36106433 | 2022 | PDF local | Revisão focada; usar obrigatoriamente com REF-NSGC-2025. |
| REF-NSGC-2025 | French, Bennett, Resta. DOI [10.1002/jgc4.2020](https://doi.org/10.1002/jgc4.2020); PMID [40114506](https://pubmed.ncbi.nlm.nih.gov/40114506/); PMCID PMC11926493 | 2025-03-21 | XML integral local | Correção confirmada; prevalece sobre figuras 4–5 de 2022. |
| REF-GA4GH-PED | [GA4GH Pedigree](https://www.ga4gh.org/product/pedigree/) e [repositório](https://github.com/ga4gh/pedigree) | Produto v1.0; PDAP “Draft”; consulta 2026-10-30 | README local + web | Modelo conceitual útil, porém ainda em desenvolvimento. Não é norma gráfica. |
| REF-PHENO-2 | [GA4GH Phenopacket Schema](https://phenopacket-schema.readthedocs.io/en/latest/) | release 2.0.0; documentação v2 | Web oficial | Intercâmbio fenotípico; confirmado. |
| REF-HPO-2024 | Gargano et al. DOI 10.1093/nar/gkad1005 | artigo 2024 | PDF local, CC BY 4.0 | Contexto e interoperabilidade. |
| REF-HPO-DATA | [HPO](https://hpo.jax.org/) / [releases](https://github.com/obophenotype/human-phenotype-ontology/releases) | versão deve ser gravada por projeto/importação | Web oficial | Termos e anotações mudam; não embutir cópia sem versão/licença. |
| REF-ORPHA | [Orphanet nomenclature pack](https://www.orphadata.com/orphanet-nomenclature-for-coding/) | consulta 2026-10-30 | Web oficial | ORPHAcode para doenças raras; confirmar versão do pacote a cada importação. |
| REF-HGVS | [HGVS Nomenclature](https://hgvs-nomenclature.org/stable/versions/) | 21.1.5, 2026-09-17; CC0 | Web oficial | Sintaxe de variantes. Provedor e consumidor devem declarar versão suportada. |
| REF-ACMG-2015 | Richards et al. DOI [10.1038/gim.2015.30](https://doi.org/10.1038/gim.2015.30); PMID 25741868; PMCID PMC4544753 | 2015 | PMC oficial | Cinco classes germinativas; não automatizar diagnóstico. |
| REF-CLINGEN-SVI | [ClinGen Variant Classification Guidance](https://www.clinicalgenome.org/tools/clingen-variant-classification-guidance/) | página atualizada jul/2025 | Web oficial | Especificações vigentes para critérios ACMG/AMP, inclusive PP1/BS4, PS2/PM6 e PM3. |
| REF-PRIV-LGPD | Lei 13.709/2018, [texto oficial](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm) | texto vigente deve ser revisto antes da distribuição | Fonte estatal | Dados genéticos e de saúde são dados pessoais sensíveis; requisitos jurídicos requerem revisão profissional. |

## Ordem de precedência

1. Correções/erratas prevalecem sobre o artigo corrigido.
2. Revisão NSGC mais recente prevalece apenas no escopo explicitamente revisado; 1995/2008 continuam aplicáveis ao restante.
3. Uma regra gráfica NSGC não deve ser inferida de GA4GH, HPO, HGVS ou ACMG/AMP.
4. Modelos em “draft” são perfis experimentais versionados, nunca apresentados como norma consolidada.

## Pendências rastreadas

- `PEND-001`: obter PDF oficial da correção de 2025 se um endpoint licenciado permitir; o XML integral é suficiente para texto e figuras referenciadas, mas não equivale ao PDF paginado.
- `PEND-002`: revisar o GA4GH Pedigree no início da Fase 3; status e schema podem mudar.
- `PEND-003`: realizar revisão jurídica LGPD e de política institucional antes de uso clínico.
- `PEND-004`: validar o catálogo visual contra as figuras corrigidas com especialista em aconselhamento genético antes de declarar conformidade.

