# RarePedigree Studio

Aplicativo científico para criação e análise responsável de heredogramas. As **Fases 1–3** estão concluídas e a **Fase 4 possui um protótipo desktop funcional** com canvas, símbolos básicos, relações, propriedades, undo/redo, persistência JSON e exportação científica.

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

Os PDFs originais permanecem em `Artigos/`. `literature/` contém cópias organizadas e material aberto obtido durante a auditoria. Nenhum arquivo contém dados reais de pacientes.

## Desenvolvimento

```bash
conda env create -f environment.yml
conda activate rarepedigree-studio
pytest
ruff check .
rarepedigree-studio
```

**Estado:** primeira iteração da Fase 4 validada. Consulte as limitações antes de usar; o software ainda não deve ser empregado como ferramenta diagnóstica ou em produção clínica.
