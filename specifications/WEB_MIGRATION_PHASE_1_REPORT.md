# RarePedigree Studio — Migração Web, Etapa 1

Data: 4 de novembro de 2026.

## Resultado

Foi criada uma aplicação Web independente em `web/`, preservando integralmente o aplicativo PySide6 e o motor científico atual. A primeira entrega implementa a Welcome Screen aprovada conceitualmente com uma cena WebGL real, e não uma imagem ou simulação bidimensional.

## Tecnologias

- React 19 e TypeScript.
- Vite para desenvolvimento e build.
- Three.js e React Three Fiber para WebGL.
- Drei para materiais, ambiente e elementos auxiliares.
- Framer Motion para transições da interface.
- Vitest e Testing Library.

## Cena 3D

A cena contém nove indivíduos distribuídos em três gerações e em profundidades distintas. Os símbolos são geometrias tridimensionais com espessura, transmissão, rugosidade, metalness e clearcoat. As relações são cilindros orientados espacialmente entre os pontos de origem e destino.

Foram implementados:

- câmera em perspectiva;
- planos de geração em profundidade;
- iluminação ambiente, direcional, pontual e spot;
- sombras e névoa;
- materiais de vidro, metal e terracota;
- paralaxe limitada pelo cursor;
- flutuação ambiental discreta;
- seleção e inspeção de indivíduos;
- probando e estado afetado;
- interrupção de movimento conforme `prefers-reduced-motion`.

## Interface

- Layout responsivo sem elementos do sistema operacional desktop.
- Navegação superior para Editor, Recursos e Documentação.
- Ações Nova família e Abrir projeto.
- Projetos recentes em hierarquia secundária.
- Alternância PT-BR/EN.
- Alternância de tema.
- Breakpoints para desktop, tablet e celular.

## Validação

- TypeScript: aprovado.
- Vitest: 2 testes aprovados.
- Vite production build: aprovado.
- Aplicação aberta no navegador real em `127.0.0.1`.
- Console do navegador: nenhum erro.
- PT-BR, EN e tema claro verificados por interação.
- Layout móvel verificado em 390×844.
- Seleção de indivíduo verificada diretamente na cena WebGL.

Evidências:

- `assets/web_phase_1/01_webgl_welcome.png`
- `assets/web_phase_1/02_mobile_390x844.png`
- `assets/web_phase_1/03_mobile_actions_recent.png`

## Desempenho e bundle

A cena 3D é carregada de forma assíncrona, separada do shell principal. O build atual produz aproximadamente:

- shell principal: 357 kB minificado, 114 kB gzip;
- cena 3D: 956 kB minificado, 264 kB gzip.

O tamanho da cena deve ser refinado nas próximas etapas com redução de dependências Drei, carregamento progressivo e política de qualidade baseada no dispositivo.

## Limitações declaradas

- Os botões ainda não chamam o motor Python.
- Os projetos recentes são dados demonstrativos.
- Não existe autenticação, persistência Web ou backend nesta etapa.
- A cena mostra um heredograma sintético e não deve ser interpretada como dado clínico real.
- O editor científico ainda é o aplicativo PySide6.

## Próxima etapa recomendada

1. Criar API FastAPI sobre os serviços de domínio existentes.
2. Definir contrato JSON versionado para projeto, indivíduo e relação.
3. Conectar abertura/criação de projetos ao backend.
4. Migrar o editor como SVG/Canvas 2D mantendo o 3D somente como apresentação.
5. Adicionar testes end-to-end e avaliação de desempenho em GPU integrada.
