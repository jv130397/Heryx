# Requisitos iniciais

## Funcionais

- `FR-01..06`: criar/editar indivíduos, identidade separada, estados fenotípicos, vital status, papéis e portadores conforme PED-001..007.
- `FR-07..15`: representar tempo clínico, relações, consanguinidade, separação/divórcio, gêmeos, adoção, eventos reprodutivos, ART e anotações sem glifo normativo.
- `FR-16`: registrar genes, variantes HGVS, assembly/transcrito, zigosidade, fase, mosaicismo, de novo e segregação com proveniência.
- `FR-17`: registrar HPO presente, explicitamente ausente ou desconhecido; atualizar vocabulário sem alterar dados históricos.
- `FR-18`: manter observação, hipótese diagnóstica e inferência computacional em camadas diferentes.
- `FR-19`: salvar/reabrir projeto local com migração versionada e backup transacional.
- `FR-20`: importar PED/FAM de modo conservador, gerar relatório de perdas e nunca inventar relações/sexo/gênero.
- `FR-21`: exportar JSON nativo, SVG/PNG/PDF e perfis Phenopacket; exportação anonimizada deve ser uma ação explícita e auditável.
- `FR-22`: validar estrutura (ciclos parentais impossíveis, duplicatas, relações incompletas) e emitir severidade, fonte da regra e correção sugerida.
- `FR-23`: desfazer/refazer por comandos sem corromper o grafo; auto-layout atua somente em `Layout`.
- `FR-24`: gerar legenda com cada padrão/cor/anotação realmente usada.

## Não funcionais e privacidade

- `NFR-01` offline-first; nenhuma telemetria clínica por padrão.
- `NFR-02` pseudonimização, minimização, finalidade e retenção configuráveis; dados genéticos/saúde tratados como sensíveis sob LGPD.
- `NFR-03` temporários em diretório privado, limpeza segura na saída e exportação atômica.
- `NFR-04` nunca executar macros, scripts ou conteúdo ativo importado; limites de tamanho/profundidade e parser defensivo.
- `NFR-05` SQLite com integridade referencial, WAL/backup e opção futura de criptografia avaliada por threat model; não prometer criptografia antes da seleção/validação.
- `NFR-06` reprodutibilidade: schema, terminologias, HGVS, regras e algoritmos versionados no projeto.
- `NFR-07` acessibilidade: teclado, contraste, padrões além de cor e tema claro/escuro.
- `NFR-08` avisos: ferramenta de documentação/análise, não diagnóstico autônomo; inferências requerem revisão profissional.
- `NFR-09` testes sintéticos apenas; nenhum dado real de paciente no repositório.
- `NFR-10` arquivos exportados incluem aviso de sensibilidade e opção de remoção de datas/IDs/notas.

## Critérios de aceite da especificação

- Toda regra renderizada aponta para `PED-*` e pelo menos um teste.
- Estados desconhecidos sobrevivem a salvar/carregar/exportar.
- Alterar posição gráfica não altera nenhum fato clínico/genético.
- Fontes externas indisponíveis não impedem abrir projetos; termos já usados permanecem visíveis com versão.

