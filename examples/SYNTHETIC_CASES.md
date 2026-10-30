# Casos sintéticos planejados

Todos os IDs, idades e achados são fictícios. Estes roteiros são especificações de teste, não casos clínicos nem diagnósticos.

| Caso | Estrutura | Fatos controlados | O que deve ser verificado | Cautela |
|---|---|---|---|---|
| SYN-AD-3GEN | 3 gerações, 9 pessoas | fenótipo presente em gerações sucessivas; variante heterozigota em parte dos afetados | layout, legenda, estados não testados e segregação PP1 apenas se requisitos forem fornecidos | aparência “dominante” é hipótese |
| SYN-AR-CONS | primos com 2 descendentes | variantes em trans confirmadas em um descendente; consanguinidade | linha dupla, fase, PM3 e portadores por padrão/legenda sem ponto | não inferir portador nos não testados |
| SYN-XLINK | 3 gerações | variante no X, hemizigose e heterozigose explicitamente medidas | genótipo separado de gênero/sexo; transmissão possível | sem linguagem determinista |
| SYN-MTDNA | linhagem materna sintética | heteroplasmia medida com fração e tecido | anotação mtDNA, proveniência de amostra e incerteza | não inferir intensidade clínica pela fração isolada |
| SYN-TWINS | gêmeos MZ e par DZ em ramos distintos | zigosidade conhecida por evidência; outro grupo desconhecido | ramos, linha MZ, estado desconhecido | não deduzir zigosidade pela aparência |
| SYN-DENOVO | trio | variante no probando; confirmação parental configurável | PS2 versus PM6 conforme confirmação e fenótipo | “de novo” é evidência, não causalidade automática |
| SYN-INCOMP-PEN | 3 gerações | variante presente em indivíduo sem manifestação à idade registrada | separar genotype, phenotype e idade | não rotular “não afetado” sem condição/tempo |
| SYN-MOSAIC | trio + amostras | VAF diferente em sangue e outro tecido | amostra, método, VAF e anotação; nenhum glifo inventado | limite técnico do ensaio deve ser visível |
| SYN-ADOPTION-ART | adoção + gamete donor + gestational carrier | relações biológicas, sociais e gestacionais distintas | colchetes, D/G, linhas tracejadas e correção 2025 | não colapsar “parent” em um único campo |
| SYN-INCOMPLETE | 3 gerações parcialmente conhecidas | datas, gênero, fenótipo e genótipos ausentes por motivos distintos | round-trip de unknown/not_asked/withheld/not_tested | ausência de dado não é negativo |
| SYN-PREG-OUTCOMES | múltiplos eventos reprodutivos | gestação atual, SAB, TOP, ECT e stillbirth | símbolos da Fig.4 corrigida, idade gestacional e privacidade | terminologia sensível e configurável |

Nenhum padrão acima será apresentado como diagnóstico confirmado. A geração de fixtures executáveis fica para as Fases 3–4, depois da aprovação do schema.

