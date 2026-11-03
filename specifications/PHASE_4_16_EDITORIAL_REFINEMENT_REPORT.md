# RarePedigree Studio — Refinamento editorial da Welcome Screen

Data: 3 de novembro de 2026.

## Motivo da revisão

A composição anterior estava tecnicamente correta, mas utilizava elementos muito associados a interfaces genéricas de tecnologia: esfera de partículas, azul neon, cartões grandes e texto promocional. A revisão substitui essa linguagem por uma apresentação específica do domínio de genética clínica.

## Alterações aplicadas

- A Genomic Sphere deixou de ser exibida na Welcome Screen.
- O elemento central agora é um heredograma clínico assimétrico com três gerações, nove indivíduos, probando, indivíduo afetado e sexo não especificado.
- O heredograma é construído progressivamente durante a entrada.
- As conexões usam linhas ortogonais, uniões alinhadas e faixas de geração identificadas à esquerda.
- O hover destaca um indivíduo sem deslocar a geometria e mostra identificador e papel familiar.
- A animação ociosa foi reduzida a uma pulsação muito discreta no item inspecionado.
- A paleta neon foi substituída por carvão, papel, azul acinzentado e terracota clínica.
- A tipografia de títulos ganhou caráter editorial, mantendo a fonte de interface nos controles.
- Os textos publicitários foram substituídos por linguagem objetiva de produto científico.
- “Projetos recentes” passou a ter hierarquia secundária e deixou de competir visualmente com Nova família e Abrir projeto.
- A barra de menu nativa continua oculta na tela inicial.
- Os temas Midnight e Light, PT-BR/EN e movimento reduzido foram preservados.

## Convenções visuais

O desenho introdutório é demonstrativo e não modifica projetos ou dados do usuário. Quadrado, círculo e losango mantêm as convenções já utilizadas pelo editor. O probando recebe seta, o estado afetado usa preenchimento e os rótulos I, II e III permanecem no extremo esquerdo.

Os cônjuges e irmãos foram alinhados na mesma faixa horizontal para evitar linhas inclinadas e interpretações ambíguas.

## Arquivos

- `src/rarepedigree/ui/living_pedigree.py`
- `src/rarepedigree/ui/home.py`
- `src/rarepedigree/ui/theme.py`
- `src/rarepedigree/ui/i18n.py`
- `tests/unit/test_phase_4_16_editorial_welcome.py`
- `scripts/validate_phase_4_16_editorial.py`

O componente `GenomicSphere` foi mantido no repositório para compatibilidade com as evidências e testes da Fase 4.16.0, mas não participa da tela inicial atual.

## Testes

```text
conda run -n rarepedigree-studio ruff check .
QT_QPA_PLATFORM=offscreen conda run -n rarepedigree-studio pytest -q
```

Resultado:

- Ruff: aprovado.
- Pytest: **187 testes aprovados em 8,64 s**.
- Quatro novos testes verificam símbolos clínicos, probando, hover sem deslocamento, movimento reduzido e hierarquia secundária de projetos recentes.

## Evidências reais

- `assets/phase_4_16_editorial/01_editorial_pt_1920x1080.png`
- `assets/phase_4_16_editorial/02_editorial_pt_1366x768.png`
- `assets/phase_4_16_editorial/03_clinical_hover.png`
- `assets/phase_4_16_editorial/04_reduced_motion.png`
- `assets/phase_4_16_editorial/05_editorial_en_light.png`

As imagens foram obtidas diretamente com `QWidget.grab()` da aplicação PySide6, sem composição posterior.

## Aceitação

O refinamento é aceito: a Welcome Screen agora comunica a função do RarePedigree Studio por meio do próprio vocabulário gráfico de heredogramas, reduzindo substancialmente a aparência de landing page genérica.

