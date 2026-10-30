# Modelo de dados conceitual

Princípios: grafo familiar independente do layout; fatos observados separados de hipóteses e inferências; ausência não equivale a normalidade; toda terminologia externa leva versão e procedência.

## Entidades

- `Project`: UUID, schema_version, datas, configurações de privacidade, terminologias e versões.
- `Family`: UUID, identificador pseudônimo, membros e notas com controle de acesso.
- `Individual`: UUID interno, family_id, identificadores pseudônimos, geração/posição apenas como preferência de layout, datas/idades com precisão, vital status.
- `IdentityAttributes`: identidade de gênero, sexo atribuído ao nascimento, características cromossômicas/cariótipo e VSC em campos independentes, cada qual com `known/unknown/not_asked/withheld/not_applicable`, fonte e consentimento de exibição.
- `Relationship`: participantes, tipo biológico/social/legal, intervalo temporal, certeza e fonte. Não usar apenas “pai/mãe”: suportar `egg_parent`, `sperm_parent`, gestational carrier e parentagem social.
- `TwinGroup`: membros, zigosidade conhecida/desconhecida e evidência.
- `ReproductiveEvent`: tipo, gestational carrier, contribuintes de gametas, idade gestacional, desfecho e observações.
- `PhenotypicObservation`: HPO ID + label preservado, presente/ausente/desconhecido, início, resolução, severidade, método, observador, data e fonte. Negação é explícita.
- `ClinicalHypothesis`: diagnóstico suspeito/diferencial/confirmado, código MONDO/ORPHA/OMIM quando licenciado, status, autor e evidência.
- `GeneAssessment`: HGNC ID/símbolo, escopo e resultado da investigação.
- `Variant`: HGVS original e normalizado, referência (RefSeq/LRG), assembly, coordenadas opcionais, alelos e versão HGVS.
- `GenotypeObservation`: indivíduo/amostra, variante(s), zigosidade, fase cis/trans/desconhecida, mosaic fraction, método, qualidade e origem germinativa/somática/mtDNA.
- `VariantInterpretation`: classe ACMG/AMP, condição, laboratório/curador, data, guideline/version, critérios/evidências; nunca sobrescreve o achado observado.
- `SegregationEvidence`: pedigree scope, meioses informativas, indivíduos incluídos, PP1/BS4/PS2/PM6/PM3 quando aplicável, limitações e conclusão computacional separada.
- `Inference`: algoritmo/versão, entradas, saída, confiança, timestamp e aprovação humana.
- `Layout`: coordenadas, zoom, ordem e rotas de linhas; descartável e sem autoridade clínica.
- `Provenance`: source_type, locator, author, acquired_at, checksum e license.

## Invariantes

1. IDs clínicos externos nunca são chave primária.
2. Excluir observação não exclui o indivíduo; apagar layout não apaga relações.
3. `unknown`, `not_tested`, `not_asked`, `withheld` e `negative` são valores distintos.
4. “Não afetado” exige condição e tempo de referência; não é default.
5. De novo exige estado de confirmação de maternidade/paternidade genética e critérios ClinGen; caso contrário é hipótese.
6. Heterozigose composta exige duas variantes e fase; `phase=unknown` impede afirmação em trans.
7. Dados importados preservam valor original e relatório de transformação.
8. Exportação Phenopacket é perfil versionado e com perdas documentadas; GA4GH Pedigree fica experimental enquanto draft.

