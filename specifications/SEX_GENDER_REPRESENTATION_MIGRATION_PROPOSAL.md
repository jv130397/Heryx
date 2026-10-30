# Proposta de migração: sexo, gênero e representação no heredograma

## Estado e decisão da Fase 4.7.1

Este documento é uma proposta; nenhuma migração estrutural foi executada. O campo legado
`gender_identity` continua sendo lido e gravado sem alteração para preservar projetos 0.1/0.2.
Hoje ele também determina o formato gráfico, o que mistura um dado declarado com uma convenção
de representação.

## Modelo candidato

- `sex_assigned_at_birth`: dado clínico opcional, com ausência explicitamente representável.
- `gender_identity`: identidade declarada opcional, sem inferência a partir do símbolo.
- `pedigree_symbol`: escolha de apresentação independente (`square`, `circle`, `diamond`).
- Proveniência, data e grau de certeza devem acompanhar dados clínicos quando aplicável.

As cores permanecem estritamente decorativas. O estado fenotípico continua representado por
preenchimento e nunca deve ser inferido da cor do contorno.

## Migração futura proposta

1. Introduzir os campos novos como opcionais em uma nova versão do esquema.
2. Preservar `gender_identity` legado e derivar apenas uma sugestão visual reversível.
3. Nunca preencher sexo ou identidade por inferência automática.
4. Manter leitura e round-trip dos esquemas 0.1 e 0.2.
5. Exigir testes de migração, exportação e regressão visual antes de remover o campo legado.

## Critérios antes da implementação

- revisão formal das convenções de heredogramas adotadas pelo projeto;
- validação por profissional de genética clínica;
- definição de terminologia PT-BR/EN e política de dados ausentes;
- fixtures anonimizadas para todos os casos e teste de compatibilidade retroativa.
