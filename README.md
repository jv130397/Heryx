# RarePedigree Studio

Aplicativo científico para criação e análise responsável de heredogramas. A **Fase 4.6**
refina a RarePedigree Scientific Workspace com toolbar compacta, rail de ferramentas, estado
vazio funcional, propriedades contextuais e design system próprio.

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

Os PDFs originais permanecem em `Artigos/`. `literature/` contém cópias organizadas e material aberto obtido durante a auditoria. Nenhum arquivo contém dados reais de pacientes.

## Desenvolvimento

```bash
conda env create -f environment.yml
conda activate rarepedigree-studio
pytest
ruff check .
rarepedigree-studio
```

**Estado:** Fase 4.6 validada. Consulte as limitações antes de usar; o software ainda não deve
ser empregado como ferramenta diagnóstica ou em produção clínica.
