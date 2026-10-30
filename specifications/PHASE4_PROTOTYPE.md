# Fase 4 — Protótipo funcional

Data de validação: 2026-10-30.

## Recursos implementados

- Janela desktop PySide6 com menu, toolbar, canvas e painel de propriedades.
- Símbolos básicos confirmados: quadrado, círculo e losango; afetado, não afetado, desconhecido, falecido, proband e consultand.
- Criação, seleção por área, arrastar e zoom (`Ctrl` + roda do mouse).
- Relação de parceria e consanguinidade entre exatamente duas pessoas selecionadas.
- Desfazer/refazer para criação, relação, movimento e edição de propriedades.
- Projeto JSON nativo versionado, validação Pydantic, limite de 20 MiB e gravação atômica com permissão `0600`.
- Exportação SVG, PNG em alta resolução e PDF.
- Funcionamento local, sem rede ou telemetria.

## Limites deliberados

- Não há ainda descendência, sibship, gêmeos, adoção, ART, eventos gestacionais ou auto-layout. Esses recursos exigem comandos e validações próprias.
- Portadores e múltiplos padrões de preenchimento aguardam um editor de legenda; o antigo ponto central não foi implementado.
- Sexo atribuído ao nascimento e identidade de gênero não são confundidos; este protótipo expõe apenas a identidade usada para escolher a forma. Os outros atributos serão adicionados como campos separados.
- Não há diagnóstico, cálculo automático de padrão de herança ou classificação ACMG/AMP.
- SQLite, migrações e recuperação de sessão permanecem para a próxima iteração; JSON é o formato ativo do protótipo.
- O PDF usa a página padrão do Qt e ainda não oferece configuração editorial de tamanho/margens.

## Uso

```bash
conda activate rarepedigree-studio
rarepedigree-studio
```

Adicione indivíduos pela barra de ferramentas. Selecione dois com `Ctrl` e escolha **Relacionar selecionados**. Selecione uma pessoa para editar suas propriedades. Projetos usam a extensão sugerida `.rps.json`.

## Verificação

- `ruff check .`
- `QT_QPA_PLATFORM=offscreen pytest`
- Oito testes automatizados cobrem fronteiras arquiteturais, estados desconhecidos, modelos, persistência, renderização/exportação e undo/redo.
- Inspeção visual headless realizada em 1180×760 com símbolos sintéticos; nenhuma informação real foi usada.

