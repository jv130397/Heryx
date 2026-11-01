# Fase 4.10.2 — Auditoria das referências em `Modelos/`

## Escopo e método

A pasta real encontrada é `Modelos/` (plural e com inicial maiúscula). O inventário foi produzido recursivamente em 1º de novembro de 2026 com `find`, `file` e SHA-256. Cada PNG foi aberto em resolução integral; o MP4 já havia sido decodificado quadro a quadro na Fase 4.10.1 e foi revalidado como o mesmo arquivo pelo hash. Nenhum arquivo original foi modificado ou incluído no Git.

## Inventário completo

| Caminho relativo | Formato/dimensões | Tamanho | Modificação | SHA-256 | Inspeção/finalidade aparente |
|---|---:|---:|---|---|---|
| `heredograma_linkedin.mp4` | MP4/H.264, 1280×720, 30 fps, 46,1 s | 1.208.437 B | 2026-11-01 11:23 | `105e02f96efcc41136bb23418086a4490702d944f064f2260934fe0adc2e9df8` | Inspecionável; visão geral promocional do Open Pedigree X 1.3 |
| `Imagem colada.png` | PNG RGBA, 1920×1080 | 161.785 B | 2026-11-01 11:43 | `120d6e6c6d2830f1824669ab7bd7f53a3e4c920fc7f031ca90a84ed79c4d3c45` | Editor contextual, aba Pessoal |
| `Imagem colada (2).png` | PNG RGBA, 1920×1080 | 152.633 B | 2026-11-01 11:43 | `3502b7481da6c5a52e522d74ad8a014881eaa5357905e9ff108916cdd34a6c56` | Editor contextual, aba Clínico |
| `Imagem colada (3).png` | PNG RGBA, 1920×1080 | 124.016 B | 2026-11-01 11:44 | `2bc3b1813f935106d1049565054b874651df29892147fca8c3e4ebbf9672fb4c` | Criação de parceiro, handles próximos à relação |
| `Imagem colada (4).png` | PNG RGBA, 1920×1080 | 126.127 B | 2026-11-01 11:44 | `efa0f1a652385f7ffc453da42c335fee917a7b2cc52655651de8a54ffff00ff4` | Ação contextual de descendência |
| `Imagem colada (5).png` | PNG RGBA, 1920×1080 | 127.832 B | 2026-11-01 11:45 | `07c1b04352ecd362b7395a69dc0d17f5a80148376f6e864a9af7e8cdaff311fe` | Toolbar contextual de tipo/quantidade de descendentes |
| `Imagem colada (6).png` | PNG RGBA, 1920×1080 | 147.511 B | 2026-11-01 11:45 | `6a4284de990b770e3c94f9f435bf7abc198f82818b5b2e7e4f30b8c6b049ebc2` | Dropdown de ferramentas com ícones e ação destrutiva separada |
| `Imagem colada (7).png` | PNG RGBA, 1920×1080 | 178.621 B | 2026-11-01 11:46 | `f9e89d7d8c0ae1f692a58fd291e267c9a5177b000319a541f46e25e76e28aaf0` | Modal de opções de rótulo e numeração genealógica |
| `Imagem colada (8).png` | PNG RGBA, 1920×1080 | 179.556 B | 2026-11-01 11:46 | `302499fcda9def9f842eb5b354d260ea9f786dbf82dea0249b3d608de3323abd` | Modal largo de testes/diagnóstico |
| `Imagem colada (9).png` | PNG RGBA, 1920×1080 | 187.390 B | 2026-11-01 11:47 | `09bf3adb44ac59bc565e3e7449ca10c69b06fe4c0f7824977526b6a8e6bd81f8` | Modal de exportação com formato e privacidade |
| `Imagem colada (10).png` | PNG RGBA, 1920×1080 | 138.215 B | 2026-11-01 11:48 | `2c9643a069ba643e1115c489545503ecd13a0ea0b4ecbef4d62eabba893a0725` | Popover de paleta e estado selecionado no canvas |

## Elementos relevantes e aplicação

| Referência | Elementos relevantes | Aplicação proposta | Prioridade |
|---|---|---|---|
| `Imagem colada.png` | Painel contextual próximo ao indivíduo, abas, campos compactos | Refinar inspector e formulários sem criar painel fixo | Alta |
| `Imagem colada (2).png` | Separação explícita entre dados pessoais e clínicos | Manter aba Clínica reservada ao que o domínio já suporta | Média |
| `Imagem colada (3).png` | Ações no contexto da relação, seleção com halo discreto | Preservar menu contextual sem encobrir símbolos | Média |
| `Imagem colada (4).png` | Handle de descendência ancorado à união | Referência para ações contextuais futuras; não alterar motor nesta fase | Baixa |
| `Imagem colada (5).png` | Popover horizontal com ícones grandes e alvo adequado | Melhorar densidade dos menus de criação | Média |
| `Imagem colada (6).png` | Menu branco, ícones alinhados, separador antes de destruição | Aplicar aos menus e dropdowns Qt | Alta |
| `Imagem colada (7).png` | Modal proporcional, backdrop, configuração de rótulo e numeração | Implementar preferência de rótulo genealógico separada do ID | Alta |
| `Imagem colada (8).png` | Modal largo, cabeçalho marinho, seções e ações inferiores | Consolidar padrão para diálogos complexos | Média |
| `Imagem colada (9).png` | Exportação: formatos, privacidade, ações claras | Refinar apresentação da exportação existente, sem prometer formatos inexistentes | Média |
| `Imagem colada (10).png` | Popover de cores, amostras circulares, seleção cinza translúcida | Referência para preferências de cor e seleção não clínica | Média |
| `heredograma_linkedin.mp4` | Shell claro, busca, modais, toolbar e canvas dominante | Manter direção adotada na 4.10.1 | Alta |

## Padrões unificados extraídos

- Canvas dominante em cinza quase branco, sem decoração competindo com o grafo.
- Toolbar compacta branca, grupos separados e alvos de aproximadamente 34–40 px.
- Azul-marinho reservado à estrutura de modais; azul/ciano reservado a foco e ação.
- Menus brancos com sombra suave, ícones à esquerda e separadores sem excesso.
- Modais centralizados com backdrop, cabeçalho escuro, corpo branco e ações no rodapé.
- Editor de pessoa dividido em dimensões pessoais e clínicas, sem misturar valores internos e rótulos.
- Identificador exibido pelo usuário separado da numeração genealógica opcional (`I-1`, `II-3`).
- Seleção deve realçar a região sem alterar o preenchimento que codifica fenótipo.

## Conflitos e decisões

As novas imagens exibem um editor web com controles contextuais diretamente sobre as relações; a referência anterior também exibe modais e busca. No RarePedigree, menus sobre o canvas podem ocultar conectores e prejudicar interpretação. A solução é manter ações principais em rail/menus Qt e usar contexto somente após seleção explícita.

O exemplo usa vermelho para uma condição clínica e borda dourada para foco. O RarePedigree preserva preenchimento científico e usa ciano apenas como seleção de interface; cores decorativas não redefinirão fenótipo.

A aba clínica da referência contém HPO e testes genéticos que pertencem a fases futuras. A interface não criará campos sem suporte no modelo atual.

## Restrições legais e técnicas

As capturas mostram Open Pedigree X, PhenoTips e uma implantação de terceiro. Não há licença ou código-fonte na pasta. Apenas padrões conceituais observáveis serão reproduzidos; marcas, textos proprietários, fontes, código, SVGs e ativos não serão copiados. Como são imagens estáticas, não é possível medir curvas ou durações reais de animação; serão mantidos os tokens de 120–220 ms já documentados.
