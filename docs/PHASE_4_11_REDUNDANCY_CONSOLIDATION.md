# Consolidação das redundâncias da interface

> Atualização de 2 de novembro de 2026: a criação familiar foi posteriormente
> concentrada integralmente na barra do indivíduo. Consulte
> `PHASE_4_11_CONTEXT_ONLY_CREATION_AND_ZOOM.md` para o estado vigente.

## Resultado

As recomendações prioritárias de `PHASE_4_11_REDUNDANCY_AUDIT.md` foram aplicadas sem alterar o domínio, o motor de parentesco, o layout científico ou o formato persistente.

## Alterações realizadas

| Área | Antes | Agora |
|---|---|---|
| Edição individual | Drawer e editor flutuante editavam os mesmos campos | Exclusivamente `FloatingIndividualEditor` |
| Drawer | Formulário individual, resumo, relações e clínica vazia | Inspector somente leitura de relações e conectores |
| Clique direito | Criação familiar, dois caminhos de edição, foco, centro e exclusão | Editar, focar, centralizar e excluir |
| Barra contextual | Concorria com rail e clique direito | Fluxo visual primário para pais, parceiro, filho e irmão |
| Rail “Adicionar familiar” | Repetia todas as ações básicas | Assistente e operações avançadas: vínculo, reconciliação, ramo, desconhecidos e adoção |
| Toolbar | Incluía auto-layout apesar do rail e menu | Auto-layout permanece no rail e menu/atalho |
| Foco no probando | Rail, menu, Ramos e atalho | Removido do rail; preservado no menu, Ramos e atalho |
| Rótulos | Dois formulários gravavam as mesmas configurações | A ação dedicada abre diretamente Preferências › Heredograma |
| Alias legado | `properties_dock` duplicava `properties_drawer` | Removido |
| QML experimental | Status implícito | Documentado em `ui_next/README.md`; não deve evoluir em paralelo |

## Acessibilidade e compatibilidade

- As ações familiares básicas continuam disponíveis no menu desktop Heredograma para navegação por teclado.
- Duplo clique, `Ctrl+I`, menu e botão contextual convergem para o mesmo editor flutuante.
- A seleção de uma conexão continua abrindo o inspector e exibindo núcleo parental, genitores, descendentes e evidência.
- A seleção de uma pessoa não abre o drawer.
- Operações avançadas permanecem no assistente familiar.
- Nenhuma chave de projeto ou entidade científica foi removida.

## Validação

Foram incluídas regressões para garantir que:

- o inspector não contenha `QLineEdit` ou `QPushButton` de edição;
- o alias `properties_dock` não exista mais;
- o rail familiar não repita pais, parceiro, filho ou irmão;
- o menu contextual exponha apenas o conjunto consolidado;
- “Configurar rótulos…” abra a única fonte de configuração.

As capturas reais da Fase 4.11 foram regeneradas, incluindo a nova aba unificada de preferências de heredograma.

## Itens deliberadamente preservados

- Menu + toolbar + atalho para operações globais como salvar, desfazer e exportar.
- Menu Heredograma como fallback acessível das ações contextuais.
- Botão de exclusão no rail até existir evidência de acionamento acidental recorrente.
- Código `ui_next` experimental, pois removê-lo exige uma decisão arquitetural independente.
