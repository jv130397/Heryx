# Inventário da literatura

**Auditoria:** 2026-10-30 · **Escopo:** árvore completa do projeto antes da criação da biblioteca.  
**Método:** `rg --files -uu`, `file`, `pdfinfo`, extração com `pdftotext`, conferência de título/DOI no texto, SHA-256 e comparação com PubMed/PMC e páginas oficiais. “Íntegro” abaixo significa tecnicamente legível, não uma autenticação criptográfica pelo editor.

## Arquivos encontrados originalmente

| ID | Arquivo original | Identificação verificada | Tema e relevância | Integridade/procedência | Regras extraíveis |
|---|---|---|---|---|---|
| LOC-001 | `Artigos/Journal of Genetic Counseling - December 1995 - Bennett - Recommendations for standardized human pedigree nomenclature.pdf` | Bennett RL et al. (1995), *Recommendations for Standardized Human Pedigree Nomenclature*, DOI [10.1007/BF01408073](https://doi.org/10.1007/BF01408073), 13 p. | Norma gráfica de base; relevância crítica | PDF 1.4, não criptografado, texto legível; SHA-256 `99d460...7d35`; cópia obtida via Wiley/CAPES segundo rodapé. Metadado de modificação 2026-10-30, portanto cadeia de custódia editorial não demonstrada. | Símbolos de pessoas, linhas, adoção, gêmeos, perdas gestacionais e reprodução assistida. Atualizar por 2008/2022/2025 quando houver conflito. |
| LOC-002 | `Artigos/Journal of Genetic Counseling - 2008 - Bennett - Standardized Human Pedigree Nomenclature  Update and Assessment of the.pdf` | Bennett RL, French KS, Resta RG, Doyle DL (2008), DOI [10.1007/s10897-008-9169-9](https://doi.org/10.1007/s10897-008-9169-9), PMID 18792771, 10 p. | Atualização dos símbolos e genótipos; crítica | PDF 1.4, legível; SHA-256 `f7fc0e...0259`; metadado de modificação 2026-10-30. | Proband/consultand, ECT, gêmeos, infertilidade, ART, portador/presintomático e anotação molecular. |
| LOC-003 | `Artigos/Journal of Genetic Counseling - 2022 - Bennett - Practice resourcefocused revision  Standardized pedigree nomenclature.pdf` | Bennett RL et al. (2022), *Practice resource-focused revision...*, DOI [10.1002/jgc4.1621](https://doi.org/10.1002/jgc4.1621), PMID 36106433, 11 p. | Sexo/gênero e portadores; crítica | PDF 1.7, legível; SHA-256 `db5ab2...4edb`; metadado de modificação 2023-12-04. Deve ser lido com a correção de 2025. | Forma representa gênero; sexo atribuído separado; abandona ponto de portador; padrões de preenchimento/legenda. |
| LOC-004 | `Artigos/gkad1005.pdf` | Gargano MA et al. (2024), *The Human Phenotype Ontology in 2024*, DOI [10.1093/nar/gkad1005](https://doi.org/10.1093/nar/gkad1005), 14 p. | HPO, internacionalização e Phenopackets; alta | PDF OA CC BY 4.0, legível e marcado; SHA-256 `04160b...5990`. O `file` reporta 10 páginas, mas `pdfinfo` confirma 14; prevalece `pdfinfo`. | Fenótipos por identificador HPO, interoperabilidade e atualização versionada da ontologia. |

Não havia DOCX, TXT, Markdown, imagens avulsas, PED, FAM ou JSON. Os arquivos originais em `Artigos/` foram preservados sem alteração. Cópias normalizadas foram colocadas em `literature/`.

## Materiais obtidos durante a auditoria

| ID | Arquivo | Fonte/licença | Estado |
|---|---|---|---|
| WEB-001 | `literature/01_NSGC_Nomenclature/French_2025_correction.xml` | Europe PMC/PMC11926493; CC BY-NC-ND 4.0; DOI 10.1002/jgc4.2020; PMID 40114506 | Texto integral JATS, legível; PDF oficial não foi obtido pelos endpoints automatizados (403/404). |
| WEB-002 | `literature/02_GA4GH_Pedigree/GA4GH_pedigree_README.md` | repositório oficial GA4GH, commit consultado `0555e135...` | Snapshot textual; o produto declara v1.0, mas ainda “Draft” no PDAP. Não congelar o modelo como norma final. |

## Lacunas

- Não foram redistribuídas figuras dos artigos NSGC: as licenças dos PDFs locais não autorizam presumidamente extração/republicação.
- ACMG/AMP 2015 (PMCID PMC4544753), Phenopackets 2.0, HGVS 21.1.5, ClinGen SVI e Orphanet foram verificados por fontes oficiais, mas permanecem como links/versiones no registro; downloads automatizados indisponíveis ou desnecessários para a especificação inicial.
- Nenhum exemplo clínico local foi encontrado. Os exemplos futuros devem ser inteiramente sintéticos.

