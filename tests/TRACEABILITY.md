# Matriz de rastreabilidade de testes

Plano mínimo para cada regra normativa tecnicamente testável.

| Regras | Teste futuro | Tipo |
|---|---|---|
| PED-001..003 | formas/atributos independentes e round-trip sem inferência | domínio + golden SVG |
| PED-004, PED-007..008 | estados clínicos e múltiplos padrões com legenda completa | domínio + golden SVG |
| PED-005..006 | falecimento, proband e consultand com precondições | regras + golden SVG |
| PED-009..013 | estrutura de linhas, ordem, consanguinidade, gêmeos e adoção | grafo + golden SVG |
| PED-014..015 | cada evento reprodutivo e ECT corrigida | parametrizado + golden SVG |
| PED-016..018 | D/G, ART e rejeição de símbolo de embrião congelado | regras + golden SVG |
| PED-019..020 | genótipo não altera fenótipo; inferência não vira diagnóstico | domínio + segurança |
| FR-19..23 | persistência, importação conservadora, exportação e undo/redo | integração/round-trip |
| NFR-01..10 | rede ausente, temporários, entradas hostis, anonimização e acessibilidade | integração + revisão |

Golden tests devem comparar SVG normalizado (estrutura, sem depender de timestamps) e ser revisados contra as fontes licenciadas, sem copiar figuras para o repositório.
