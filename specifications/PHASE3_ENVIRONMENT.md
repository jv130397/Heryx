# Diagnóstico e ambiente da Fase 3

Data: 2026-10-30.

## Host observado

- Ubuntu 26.04.1 LTS, kernel 7.0.0-38, x86_64.
- Python do sistema 3.14.4; `pip3`, Qt 6 e CMake ausentes.
- Conda 26.5.3 com solver libmamba disponível em `/home/vitor/miniconda3`.
- Git disponível; pytest, uv, Poetry, AppImageTool e Flatpak Builder ausentes no host.

## Ambiente escolhido

```bash
conda env create -f environment.yml
conda activate rarepedigree-studio
pytest
ruff check .
rarepedigree-studio
```

O ambiente usa Python 3.12 e não modifica o Python do Ubuntu. Dependências de runtime são deliberadamente mínimas: PySide6, Pydantic e platformdirs. SQLAlchemy, Alembic, bibliotecas HGVS e empacotadores só serão adicionados após um caso de uso e teste que justifiquem a dependência.

## Estratégia de distribuição

1. Durante desenvolvimento: Conda apenas para o ambiente, pacote Python instalável via `pyproject.toml`.
2. Primeiro artefato testável: wheel local, sem prometer portabilidade de Qt.
3. Distribuição desktop: avaliar AppImage e pacote Debian em matriz limpa de Ubuntu; escolher somente após verificar plugins Qt, acessibilidade, assinatura e atualizações.
4. Não usar Conda como formato final para usuários clínicos.
