# Criação contextual exclusiva e simplificação da navegação

## Decisão de UX

Depois da consolidação anterior, ainda existiam caminhos concorrentes para criar familiares. A interface agora adota uma regra única:

- o primeiro indivíduo é criado pelo estado vazio central;
- familiares de uma pessoa existente são criados ao selecionar essa pessoa no heredograma;
- a barra contextual oferece pais, parceiro, descendente e irmão;
- o botão `⋯` da mesma barra abre o assistente para opções familiares avançadas.

O menu Heredograma e o rail esquerdo não repetem mais criação de indivíduos ou familiares.

## Alterações

| Área | Alteração |
|---|---|
| Rail esquerdo | Removidos “Adicionar indivíduo” e “Adicionar familiar” |
| Menu Heredograma | Removidas ações básicas de criação individual e familiar |
| Barra contextual | Mantida como origem exclusiva e adicionado acesso `⋯` ao assistente avançado |
| Minimap | Removido da interface, preferências e código de workspace |
| Zoom | Removido o controle duplicado do status; mantida uma única barra flutuante no canto inferior direito |
| Entrada de símbolos | Nova animação de 260 ms com fade e escala, usando curvas `OutCubic`/`OutBack` |
| Acessibilidade | A preferência “Reduzir movimento” desativa a animação de entrada |

## Integridade científica

A animação altera somente `opacity` e `scale` do item gráfico. Coordenadas, relações, sexo/gênero, fenótipo e dados persistidos não são modificados. A criação continua passando pelos mesmos serviços, validações e comandos undo/redo.

## Validação

- Não existe mais instância ou ação de minimapa na janela principal.
- `zoom_control` e `floating_zoom` apontam para a mesma barra real.
- A barra fica na metade inferior e dentro do viewport após redimensionamento.
- Os comandos de zoom modificam o `PedigreeView` real.
- O rail e o menu superior não contêm as quatro ações familiares básicas.
- A animação termina com opacidade e escala iguais a `1.0`.
