# ADR-001 — Python 3.12 em ambiente Conda isolado

- **Estado:** aceito em 2026-10-30
- **Contexto:** Ubuntu 26.04.1 fornece Python 3.14.4, sem pip e sem Qt. O projeto precisa de wheels Qt/PySide6 e reprodutibilidade sem alterar o Python do sistema.
- **Decisão:** usar Conda `rarepedigree-studio` com Python 3.12 e instalar o pacote em modo editável a partir de `environment.yml`.
- **Consequências:** maior compatibilidade hoje e ambiente reprodutível; exige atualização deliberada para Python 3.13/3.14 após validação das dependências.

