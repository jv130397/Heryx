# Heryx Web

Aplicação web do Heryx — Hereditary Analytics. O pacote combina a experiência científica com um editor SVG
interativo, criação inteligente de familiares, importação/exportação local e histórico de
undo/redo.

## Executar

```bash
pnpm install
pnpm dev
```

Abrir `http://127.0.0.1:5173/`.

## Validar

```bash
pnpm check
```

## Estrutura

- `src/App.tsx`: shell, navegação e estado do projeto.
- `src/PedigreeScene.tsx`: experiência tridimensional de abertura.
- `src/NewProjectMission.tsx`: assistente de criação.
- `src/WebPedigree.tsx`: renderização científica SVG.
- `src/IndividualDrawer.tsx`: edição deslizante e ações familiares.
- `src/familyOperations.ts`: regras de criação e posicionamento.
- `src/projectIO.ts`: persistência local do formato JSON.
- `public/`: manifesto, favicon e arquivos públicos.

## Recursos atuais

- Navegação e shell responsivo.
- Cena 3D com materiais físicos, câmera em perspectiva, iluminação e sombras.
- Heredograma clínico demonstrativo com três gerações.
- Hover/seleção de indivíduos.
- Paralaxe limitada pelo cursor.
- PT-BR/EN.
- Tema escuro/claro.
- Preferência de movimento reduzido.
- Criação e abertura de projetos locais.
- Editor SVG responsivo com zoom e marcadores de geração.
- Parceiros, pais, filhos e irmãos com proteção contra colisões.
- Seleção explícita de ramo em famílias com múltiplos parceiros.
- Painel deslizante de propriedades, undo/redo e salvamento.

Os dados permanecem no dispositivo e o motor científico Python/PySide6 permanece preservado.
O site ainda não deve ser usado para decisões diagnósticas.

## Publicação

Cada push na branch `main` executa testes e build e publica o diretório `web/dist` pelo GitHub
Pages. É necessário selecionar **GitHub Actions** como origem do Pages nas configurações do
repositório.

URL: <https://jv130397.github.io/Heryx/>

## Próxima integração

A migração deve manter o domínio Python como fonte de verdade e expô-lo gradualmente por uma API FastAPI. O editor científico deve ser migrado para SVG/Canvas 2D; a perspectiva 3D deve permanecer restrita à abertura e a visualizações exploratórias.
