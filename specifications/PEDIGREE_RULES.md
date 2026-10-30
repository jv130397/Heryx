# Regras de heredograma

Cada regra traz fonte, localização, confiança, estado e requisito associado. “Confirmada” significa suportada pela fonte indicada; não significa validação clínica do software.

| ID | Regra técnica | Fonte/local | Conf. | Estado | Req. |
|---|---|---|---|---|---|
| PED-001 | Quadrado, círculo e losango representam respectivamente homem/menino, mulher/menina e pessoa de gênero diverso ou gênero não conhecido/não especificado, conforme contexto e legenda. | NSGC 2022 §4.1, Fig.1; correção 2025 Fig.1 | Alta | Confirmado | FR-01 |
| PED-002 | A forma representa gênero, não sexo atribuído ao nascimento. Registrar AFAB/AMAB/UAAB separadamente; não inferir um do outro. | NSGC 2022 Box 1, §4.1 | Alta | Confirmado | FR-02 |
| PED-003 | Pessoa trans binária usa a forma de sua identidade de gênero e anotação de sexo atribuído; pessoa gênero-diversa usa losango e anotação, se pertinente/consentida. | NSGC 2022 §4.1 e resumo | Alta | Confirmado | FR-02 |
| PED-004 | Condição clínica é codificada por preenchimento/padrão definido em legenda; ausência de preenchimento não substitui um estado explícito desconhecido. | NSGC 1995 Fig.1; 2008 Fig.1; 2022 Fig.2 | Alta | Confirmado | FR-03 |
| PED-005 | Falecimento é barra diagonal sobre o símbolo; causa/idade de morte podem ser anotadas quando conhecidas. | NSGC 2008 Fig.1 item 5 | Alta | Confirmado | FR-04 |
| PED-006 | Proband é assinalado por seta e é afetado no uso NSGC; consultand é a pessoa que busca aconselhamento e recebe seta, com preenchimento somente se afetada. | NSGC 2008 Fig.1 itens 6–7; 2022 Fig.2 | Alta | Confirmado | FR-05 |
| PED-007 | O antigo ponto central não deve indicar portador. Dividir o símbolo em setores com padrões distintos e explicar cada padrão na legenda. | NSGC 2022 §4.5, Fig.2 | Alta | Confirmado; substitui 1995/2008 | FR-06 |
| PED-008 | Assintomático/pré-sintomático descreve estado clínico no tempo e deve permanecer separado de genótipo/portador. | NSGC 2008 Fig.4; 2022 Fig.2 | Alta | Confirmado | FR-07 |
| PED-009 | Relação/parceria usa linha horizontal; descendência sai da linha de relação; irmãos ligam-se à linha fraterna e são ordenados por nascimento quando conhecido. | NSGC 1995 Fig.3 | Alta | Confirmado | FR-08 |
| PED-010 | Consanguinidade usa linha dupla; grau deve ser anotado quando não evidente. | NSGC 2008 Fig.2 | Alta | Confirmado | FR-09 |
| PED-011 | Separação e divórcio devem ser atributos de relação e renderizados conforme convenção NSGC, sem apagar a relação parental/biológica. | NSGC 1995/2008 figuras de relacionamentos | Média | Confirmado, requer QA visual | FR-10 |
| PED-012 | Gêmeos partem de um ponto comum; monoziogóticos têm linha adicional entre os ramos, dizigóticos não; zigosidade desconhecida permanece explícita. | NSGC 2008 Fig.2 | Alta | Confirmado | FR-11 |
| PED-013 | Adoção usa colchetes; distinguir “adotado para dentro”, “para fora” e por parente; relação social não substitui origem biológica conhecida. | NSGC 2008 Fig.2 | Alta | Confirmado | FR-12 |
| PED-014 | Gestação, perda espontânea, interrupção, ectópica e natimorto são eventos distintos; idade gestacional e dados conhecidos podem ser anotados, sem inferir gênero/sexo. | NSGC 2008 Fig.1; 2022/2025 Fig.4 | Alta | Confirmado | FR-13 |
| PED-015 | Gravidez ectópica inclui a barra indicada na correção; a figura de 2022 omitiu-a por engano. | Correção 2025, corpo e Fig.4 | Alta | Confirmado; corrige 2022 | FR-13 |
| PED-016 | Em reprodução assistida, linha de descendência tracejada conecta doadores/gestational carrier; a gestação fica sob quem a carrega. | NSGC 2008 §ART/Fig.3; correção 2025 Fig.5 | Alta | Confirmado | FR-14 |
| PED-017 | Usar `G` para gestational carrier sem relação genética com embrião; não usar `S`. “Surrogate” designa quem fornece óvulo e carrega a gestação, mas a correção remove o símbolo S. | Correção 2025, corpo e Fig.5 | Alta | Confirmado; corrige 2022 | FR-14 |
| PED-018 | Não existe símbolo NSGC confirmado para embrião congelado; registrar como anotação estruturada/experimental, não símbolo inventado. | NSGC 2022 §4.3 | Alta | Pendente normativo | FR-15 |
| PED-019 | Genótipo molecular deve ser dado estruturado/anotação; não deduzir zigosidade, fase, de novo ou mosaicismo pela aparência clínica. | NSGC 2008 Fig.4 + HGVS/ACMG | Alta | Confirmado | FR-16 |
| PED-020 | O heredograma sugere hipóteses de herança, nunca confirma diagnóstico ou causalidade sozinho. | ACMG/AMP 2015 + decisão de segurança | Alta | Confirmado | NFR-08 |

## Divergências e limites

- **Portador:** 1995/2008 usavam ponto; 2022 o abandona. Implementar apenas a regra de 2022, mantendo importação legada marcada como ambígua.
- **Sexo/gênero:** 2008 falava em “phenotypic gender”; 2022 separa conceitos e redefine a semântica da forma. Dados cromossômicos, sexo atribuído e identidade ficam independentes.
- **Reprodução assistida:** exemplos 3–5 de 2022 continham terminologia/símbolos incorretos; aplicar a correção de 2025.
- **Mosaicismo, heterozigose composta, hemizigose e mtDNA:** não há um símbolo gráfico único confirmado nas fontes auditadas. São campos genéticos e anotações/legenda, não novos glifos.
- **Proband “sempre afetado”:** a convenção NSGC conflita com usos computacionais de “index case”. O modelo guarda papéis separados (`proband`, `consultand`, `index_case`) e o renderizador NSGC só rotula proband quando as precondições forem satisfeitas.

