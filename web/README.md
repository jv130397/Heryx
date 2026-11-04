# RarePedigree Studio Web

Primeira etapa da migração da interface para Web. Este pacote implementa a Welcome Screen com React, TypeScript e uma cena WebGL real construída com Three.js/React Three Fiber.

## Executar

```bash
pnpm install
pnpm dev
```

Abrir `http://127.0.0.1:5173/`.

## Validar

```bash
pnpm test
pnpm build
```

## Escopo atual

- Navegação e shell responsivo.
- Cena 3D com materiais físicos, câmera em perspectiva, iluminação e sombras.
- Heredograma clínico demonstrativo com três gerações.
- Hover/seleção de indivíduos.
- Paralaxe limitada pelo cursor.
- PT-BR/EN.
- Tema escuro/claro.
- Preferência de movimento reduzido.
- Lista demonstrativa de projetos recentes.

Os botões ainda são demonstrativos e não acessam arquivos reais. O motor científico Python e o aplicativo PySide6 permanecem inalterados nesta etapa.

## Próxima integração

A migração deve manter o domínio Python como fonte de verdade e expô-lo gradualmente por uma API FastAPI. O editor científico deve ser migrado para SVG/Canvas 2D; a perspectiva 3D deve permanecer restrita à abertura e a visualizações exploratórias.
