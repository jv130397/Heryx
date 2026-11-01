# `ui_next` — protótipo experimental

Esta árvore contém uma prova de conceito QML executável apenas por seu entrypoint próprio. Ela não é a interface distribuída pelo comando principal `python -m rarepedigree`, que usa `rarepedigree.ui.MainWindow`.

Não implementar novas funcionalidades de produto aqui em paralelo com a interface principal. Qualquer retomada deste protótipo exige uma decisão arquitetural explícita, plano de migração e paridade de testes. Até essa decisão, alterações devem limitar-se à preservação dos testes experimentais existentes.
