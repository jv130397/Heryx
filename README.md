# RarePedigree Studio

Aplicativo científico para criação e análise responsável de heredogramas. A **Fase 4.7**
introduz Midnight Genomics, internacionalização PT-BR/EN, cores de representação seguras,
modo científico, editor flutuante, assistente de projeto e preferências avançadas.

Leia primeiro:

- `specifications/LITERATURE_INVENTORY.md`
- `specifications/REFERENCE_REGISTRY.md`
- `specifications/PEDIGREE_RULES.md`
- `specifications/SYMBOL_CATALOG.md`
- `specifications/DATA_MODEL.md`
- `specifications/REQUIREMENTS.md`
- `specifications/ARCHITECTURE.md`
- `specifications/PHASE3_ENVIRONMENT.md`
- `specifications/PHASE4_PROTOTYPE.md`
- `specifications/PHASE_4_5_REPORT.md`
- `specifications/UI_DESIGN_SYSTEM.md`
- `specifications/PHASE_4_6_REPORT.md`
- `specifications/PHASE_4_7_REPORT.md`

Os PDFs originais permanecem em `Artigos/`. `literature/` contém cópias organizadas e material aberto obtido durante a auditoria. Nenhum arquivo contém dados reais de pacientes.

## Desenvolvimento

```bash
conda env create -f environment.yml
conda activate rarepedigree-studio
pytest
ruff check .
rarepedigree-studio
```

## Aplicação Web

O novo produto web está em [`web/`](web/README.md) e reúne a experiência 3D de abertura, o
assistente de criação de projetos e o editor SVG de heredogramas.

```bash
cd web
pnpm install --frozen-lockfile
pnpm check
pnpm dev
```

O pipeline em `.github/workflows/deploy-pages.yml` valida e publica a branch `main` no GitHub
Pages. Após habilitar **Settings → Pages → Source: GitHub Actions**, a URL será:

<https://jv130397.github.io/RarePedigree-Studio/>

**Estado:** migração Web em andamento. Consulte as limitações antes de usar; o software ainda
não deve ser empregado como ferramenta diagnóstica ou em produção clínica.
