# Fase 4.11 — Auditoria das referências

## Escopo e rastreabilidade

A pasta `Modelos/` foi novamente inventariada antes da implementação. Ela contém o mesmo vídeo e as mesmas dez imagens auditadas na Fase 4.10.2; não houve mudança de conteúdo ou hash. A auditoria integral, com dimensões e SHA-256, permanece em `specifications/PHASE_4_10_2_MODELS_AUDIT.md`. Os originais são material de referência não versionado e não foram modificados.

| Recurso | Comportamento observado | Estado anterior | Lacuna 4.11 | Solução adotada | Estado |
|---|---|---|---|---|---|
| `Imagem colada.png` | Editor próximo ao indivíduo, aba pessoal | Inspector deslizante distante | Edição exigia deslocamento visual | Editor flutuante ancorado ao símbolo | Implementado |
| `Imagem colada (2).png` | Separação pessoal/clínica | Campos misturados no inspector | Ausência da separação contextual | Abas Pessoal e Clínica; somente campos persistíveis | Parcial: modelo clínico ainda limitado |
| `Imagem colada (3).png` | Handles contextuais de relação | Menu contextual tradicional | Ações pouco descobríveis | Pontos de conexão após seleção | Implementado |
| `Imagem colada (4).png` | Criação contextual de descendência | Ação no rail/menu | Falta de prévia | Prévia descartável de símbolo e conector | Implementado |
| `Imagem colada (5).png` | Barra compacta de ações familiares | Menus separados | Fluxo fragmentado | Barra contextual filtrada semanticamente | Implementado |
| `Imagem colada (6).png` | Ações agrupadas e destrutiva separada | Menus Qt existentes | Consistência contextual | Ações familiares agrupadas sem excluir silenciosamente | Implementado |
| `Imagem colada (7).png` | Configuração de rótulo e numeração | Preferência dispersa | Sem diálogo dedicado | Diálogo para ID manual/genealógico/ambos e auxiliares | Implementado |
| `Imagem colada (8).png` | Testes e diagnóstico clínico | Sem entidade clínica correspondente | Persistência inexistente | Não simulado; exige evolução versionada do domínio | Não implementado |
| `Imagem colada (9).png` | Exportação científica | Diálogo de exportação existente | Evidência visual atualizada | Diálogo real preservado e recapturado | Verificado |
| `Imagem colada (10).png` | Paleta contextual | Cores de apresentação nas preferências | Sem modelo de condição | Não associar cor decorativa a diagnóstico | Parcial |
| `heredograma_linkedin.mp4` | Fluxo contextual e canvas dominante | Workspace Genomic Nexus | Falta de interação no contexto | Overlays locais sem painel direito permanente | Implementado |

## Decisões científicas e legais

- A prévia é exclusivamente gráfica e nunca cria indivíduos ou relações antes da confirmação.
- As operações confirmadas continuam passando pelo motor de parentesco, pelo layout e pela pilha de undo/redo existentes.
- Cor de seleção não altera fenótipo. Uma legenda de condições só será criada quando houver condições persistidas e distinguíveis no modelo.
- HPO, resultados genéticos, datas clínicas e diagnóstico não foram apresentados como funcionais: hoje não possuem representação persistente compatível no domínio.
- Foram reproduzidos padrões de interação, não marcas, ativos, código, fontes ou textos proprietários das referências.
