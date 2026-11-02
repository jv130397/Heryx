# Modelo de dados e integração HPO

## Fonte e proveniência

RarePedigree Studio utiliza exclusivamente a distribuição oficial `hp.obo`, obtida pelo PURL
`https://purl.obolibrary.org/obo/hp.obo`. O projeto oficial recomenda esse endereço em seu
[repositório](https://github.com/obophenotype/human-phenotype-ontology). A licença permite uso
mediante reconhecimento/citação, identificação da versão em exibição pública e preservação do
conteúdo e das relações da ontologia. O aplicativo não modifica termos ou relações e exibe
fonte, versão e hash da instalação.

A ontologia não é incluída no repositório. A instalação é explícita e fica no diretório de dados
do usuário, em `RarePedigreeStudio/terminology/hpo.sqlite3`.

## Índice offline

`terminology.hpo` implementa:

- parser streaming do formato OBO;
- termos, definições, sinônimos, IDs alternativos, relações `is_a`, obsolescência e substituição;
- índice SQLite FTS5 com normalização Unicode;
- busca por ID, nome e sinônimo;
- consulta de termo, filhos e metadados;
- download limitado a 64 MiB e construção em arquivo temporário;
- validação de pelo menos 10.000 termos para instalação oficial;
- `PRAGMA quick_check`, SHA-256 e substituição atômica somente após sucesso.

O download não recebe projeto, UUID, rótulo de pessoa ou qualquer dado clínico. Falhas deixam a
base instalada intacta. A operação de rede e indexação executa em `QThread`.

## Observação clínica

`HPOObservation` é armazenada em `PedigreeProject.hpo_observations` e contém:

- UUID próprio e UUID do indivíduo;
- identificador HPO e rótulo registrado historicamente;
- versão da ontologia;
- estado `present`, `absent`, `unknown` ou `not_evaluated`;
- data da observação;
- fonte e comentários;
- início, gravidade, frequência, evolução e lateralidade;
- datas de criação e atualização.

Estado fenotípico geral, observação HPO e diagnóstico são entidades distintas. Adicionar um termo
presente não marca a pessoa automaticamente como afetada. Ausência de registro aparece na matriz
como `not_evaluated`, nunca como ausência clínica.

Observações com o mesmo indivíduo, termo e data são rejeitadas. Datas diferentes preservam a
dimensão temporal. Termos obsoletos permanecem rastreáveis e apresentam a substituição oficial,
sem migração automática.

## Persistência e compatibilidade

O schema nativo evoluiu de `0.3.0` para `0.4.0`. A migração acrescenta uma lista vazia de
observações, sem criar fenótipos ou interpretar texto livre. UUIDs, parentesco, posições, notas e
preferências continuam intactos.

## Interface e transações

A aba Clínica do editor flutuante existente contém resumo, busca HPO, lista de observações,
edição e remoção. Alterações ficam em uma cópia local até Salvar. Salvar usa uma operação atômica
com undo/redo; Cancelar não toca no projeto.

O destaque por termo é temporário: verde indica presença documentada, laranja ausência
documentada, cinza desconhecido e cinza claro sem avaliação. O preenchimento científico do
símbolo não é alterado.

## Comparação e exportação

A comparação familiar trabalha apenas com observações reais. Permite seleção de pessoas,
filtros de geração e ramo materno/paterno, matriz de estados, destaque no heredograma e CSV.
Exportação é uma ação explícita e oferece identificadores pseudonimizados derivados de hash.
Nenhum arquivo temporário contém dados clínicos fora da ação solicitada.

## Limites

- Rótulos oficiais são exibidos em inglês quando não existe tradução oficial validada.
- A aplicação não afirma conformidade integral com LGPD; isso exige auditoria jurídica e de
  segurança independente.
- A versão da ontologia instalada pertence à máquina do usuário e não é embutida no projeto;
  cada observação mantém sua versão para rastreabilidade histórica.
