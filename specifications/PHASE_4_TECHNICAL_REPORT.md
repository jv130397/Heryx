# Relatório técnico do estado pós-Fase 4

**Projeto:** RarePedigree Studio  
**Auditoria:** 2026-10-30  
**Escopo:** inspeção dos arquivos reais do repositório e reexecução dos testes no ambiente Conda `rarepedigree-studio`.  
**Restrição observada:** nenhum código foi modificado durante esta auditoria; apenas este relatório foi criado.

## Resumo executivo

O repositório contém um protótipo desktop executável e coerente com o recorte declarado da primeira iteração da Fase 4. Estão funcionais: modelos mínimos de projeto, indivíduo e parceria; editor Qt Graphics View; símbolos básicos; painel de propriedades; movimentação; relações simples/consanguíneas; undo/redo; persistência JSON nativa; e exportação SVG, PNG e PDF.

HPO, HGVS, VCF, Phenopackets, PED/FAM, SQLite e análise de segregação **não estão implementados**. Há módulos reservados para genética, terminologias, intercâmbio, regras e privacidade, mas eles contêm somente docstrings. A arquitetura permite estender o sistema sem substituir o editor ou o renderizador já funcionais, desde que a Fase 5 introduza modelos e serviços por composição e preserve os UUIDs usados como referências.

Resultado reexecutado em 2026-10-30:

```text
QT_QPA_PLATFORM=offscreen pytest -q
........ [100%]
8 passed in 0.14s

ruff check .
All checks passed!
```

## 1. Estrutura atual

```text
RarePedigree-Studio/
├── Artigos/                         # quatro PDFs originalmente fornecidos
├── literature/
│   ├── 01_NSGC_Nomenclature/       # PDFs 1995/2008/2022 + correção 2025 XML
│   ├── 02_GA4GH_Pedigree/          # snapshot README GA4GH
│   ├── 03_HPO_Phenopackets/        # artigo HPO 2024
│   ├── 04_Genetic_Variants/        # reservado; vazio
│   └── 05_Clinical_Examples/       # reservado; vazio
├── examples/
│   └── SYNTHETIC_CASES.md
├── specifications/
│   ├── ARCHITECTURE.md
│   ├── DATA_MODEL.md
│   ├── LITERATURE_INVENTORY.md
│   ├── PEDIGREE_RULES.md
│   ├── PHASE3_ENVIRONMENT.md
│   ├── PHASE4_PROTOTYPE.md
│   ├── PHASE_4_TECHNICAL_REPORT.md
│   ├── REFERENCE_REGISTRY.md
│   ├── REQUIREMENTS.md
│   ├── SYMBOL_CATALOG.md
│   └── decisions/
│       ├── ADR-001-python-runtime.md
│       ├── ADR-002-layered-architecture.md
│       └── ADR-003-native-format.md
├── src/rarepedigree/
│   ├── __init__.py                  # versão 0.1.0.dev0
│   ├── __main__.py                  # entrada QApplication/MainWindow
│   ├── application/
│   │   └── commands.py              # comandos Qt undoable
│   ├── domain/
│   │   ├── models.py                # modelos Pydantic
│   │   └── states.py                # estados explícitos
│   ├── persistence/
│   │   └── json_repository.py       # JSON atômico
│   ├── rendering/
│   │   ├── exporters.py             # SVG/PNG/PDF
│   │   ├── items.py                 # símbolos e linhas
│   │   ├── scene.py                 # mapeamento domínio-cena
│   │   └── view.py                  # zoom
│   ├── ui/
│   │   ├── main_window.py
│   │   └── properties.py
│   ├── genetics/__init__.py         # reservado, sem implementação
│   ├── interchange/__init__.py      # reservado, sem implementação
│   ├── privacy/__init__.py          # reservado, sem implementação
│   ├── rules/__init__.py            # reservado, sem implementação
│   └── terminology/__init__.py      # reservado, sem implementação
├── tests/
│   ├── TRACEABILITY.md
│   └── unit/                         # oito testes coletados
├── .gitignore
├── environment.yml
├── pyproject.toml
└── README.md
```

Também existem `.pytest_cache/`, `.ruff_cache/` e `__pycache__/`, gerados localmente. O diretório analisado **não é um repositório Git** (`git status` retorna “not a git repository”), portanto não há histórico, branch ou diff auditável.

## 2. Tecnologias, bibliotecas e versões

### Versões efetivamente instaladas e verificadas

| Componente | Versão | Função atual |
|---|---:|---|
| Ubuntu | 26.04.1 LTS | host de desenvolvimento |
| Python | 3.12.16 | runtime isolado Conda |
| Conda | 26.5.3 | criação/gestão do ambiente |
| PySide6 | 6.10.3 | interface, Graphics View, undo stack e exportação Qt |
| Qt | 6.10.3 | runtime gráfico efetivo |
| Pydantic | 2.14.2 | validação e serialização do domínio |
| platformdirs | 4.14.0 | dependência instalada, mas ainda não usada pelo código |
| pytest | 9.2.0 | testes automatizados |
| pytest-qt | 4.5.0 | fixtures Qt/headless |
| Ruff | 0.17.3 | lint e ordenação de imports |
| pip | 26.2.2 | instalação editável/dependências pip no Conda |

O `pyproject.toml` declara Python `>=3.12,<3.13`, PySide6 `>=6.8,<6.11`, Pydantic `>=2.10,<3` e platformdirs `>=4.3,<5`. O build backend é Hatchling `>=1.27`, baixado no isolamento de build; ele não aparece como dependência permanente do ambiente. O pacote é instalável como `rarepedigree-studio` versão `0.1.0.dev0` e expõe o comando homônimo.

### Estado de empacotamento

- O projeto usa layout `src/` e metadados PEP 517/518.
- Um wheel puro Python foi construído na conclusão da Fase 4, mas não é mantido no repositório.
- A licença continua como `License pending`; isso bloqueia distribuição pública responsável.
- Não existem ainda AppImage, `.deb`, Flatpak, ícone ou arquivo `.desktop`.

## 3. Funcionalidades efetivamente implementadas

### Verificadas por código e/ou testes

- Inicialização de uma aplicação desktop PySide6 por `rarepedigree-studio`.
- Projeto novo em memória.
- Inclusão de indivíduo como homem/menino, mulher/menina ou gênero não especificado pela toolbar/menu.
- Opção adicional “gênero diverso” no painel de propriedades.
- Edição de rótulo, identidade usada pelo símbolo, estado fenotípico, falecimento, proband e consultand.
- Seleção simples e por rubber band; seleção de duas pessoas para criar relação.
- Relação de parceria e relação consanguínea.
- Arrastar indivíduos e atualizar as linhas conectadas.
- Zoom pelos menus e por `Ctrl` + roda, limitado entre 0,2× e 5× no evento de roda.
- Undo/redo para adicionar indivíduo, adicionar relação, mover e editar indivíduo.
- Salvar, salvar como, abrir e criar projeto novo.
- Exportar a cena como SVG, PNG ou PDF.
- Execução local sem código de rede ou telemetria.

### Planejadas, mas não implementadas

- Exclusão de indivíduos/relações.
- Descendência, linhas de sibship, gerações e ordem de nascimento.
- Separação/divórcio, adoção, gêmeos e eventos reprodutivos.
- Reprodução assistida, gestational carrier e doadores.
- Portadores por setores/padrões e legenda científica automática.
- Auto-layout, alinhamento e organização automática das gerações.
- Tema escuro, preferências persistentes e acessibilidade validada.
- SQLite, backup interno, migrações e recuperação automática.
- HPO, doenças, genes, variantes, VCF e segregação.
- Importação PED/FAM, Phenopackets ou GA4GH Pedigree.

## 4. Editor gráfico e símbolos

O editor usa `QGraphicsScene` com área fixa de 4.000 × 2.800 unidades e `QGraphicsView` com antialiasing. `PedigreeScene` mantém mapas UUID → item para pessoas e relacionamentos. Os dados de layout (`x`, `y`) ficam no modelo `LayoutPosition`, enquanto a geometria Qt fica em `IndividualItem`; antes de salvar, a janela sincroniza as coordenadas da cena.

### Símbolos implementados

| Conceito | Implementação observada | Estado |
|---|---|---|
| Homem/menino | quadrado de 48 unidades | implementado |
| Mulher/menina | círculo de 48 unidades | implementado |
| Gênero diverso | losango | implementado |
| Gênero desconhecido/não especificado | mesmo losango | implementado; visualmente indistinguível de gênero diverso |
| Afetado | preenchimento escuro | implementado |
| Explicitamente não afetado | preenchimento branco | implementado |
| Estado desconhecido | preenchimento branco com `?` | implementado |
| Falecido | barra diagonal | implementado |
| Proband | seta | implementado |
| Consultand | a mesma seta do proband | implementado, sem distinção gráfica entre os papéis |
| Parceria | linha simples entre bordas dos símbolos | implementado |
| Consanguinidade | duas linhas paralelas | implementado |

A cor azul indica seleção e não possui semântica clínica. As linhas são atualizadas ao mover pessoas e ficam atrás dos símbolos. O renderizador não implementa filhos ou linha de descendência; portanto, o resultado atual é um editor de pessoas e parcerias, ainda não um editor completo de heredogramas multigeracionais.

### Limitações de validação gráfica

- Não há golden tests de SVG nem comparação automatizada com figuras NSGC.
- O teste gráfico verifica cabeçalhos válidos de SVG/PNG/PDF, não a geometria de cada símbolo.
- `proband=True` não exige `phenotype_status=PRESENT`, embora a especificação interna registre essa precondição no perfil NSGC.
- É possível marcar simultaneamente proband e consultand; o modelo não expressa exclusividade ou precedência.
- Não há legenda, padrões de hachura, cores configuráveis nem garantia de contraste formal.
- O PDF usa configuração padrão de página do Qt, sem controle editorial de margens/tamanho.

## 5. Modelo de dados atual

### `Individual`

- `id: UUID`
- `label: str` (máximo 120 caracteres)
- `gender_identity: man | woman | gender_diverse | unknown`
- `phenotype_status: present | absent | unknown`
- `deceased: bool`
- `proband: bool`
- `consultand: bool`
- `layout: {x: float, y: float}`

O modelo usa validação em atribuição, mas ainda não contém identificador familiar, sexo atribuído ao nascimento, cariótipo, datas/idades, vital status estruturado, diagnósticos, fenótipos HPO, genes, variantes, amostras ou proveniência.

### `Relationship`

- `id: UUID`
- `member_a: UUID`
- `member_b: UUID`
- `kind: partnership | consanguineous_partnership`

Há validação para impedir relação da pessoa consigo mesma. `PedigreeProject` verifica, na validação integral, se os dois UUIDs existem. Não existem parentagem, direção, certeza, período temporal, relação social/legal, contribuição de gametas ou grupo de gêmeos.

### Projeto/família

`PedigreeProject` contém:

- `schema_version = "0.1.0"`
- `project_id: UUID`
- `title`
- `created_at` e `updated_at` em UTC
- listas de `individuals` e `relationships`

Não existe uma entidade `Family`, `family_id` ou suporte explícito a múltiplas famílias/coortes. Na prática, um arquivo representa um projeto/heredograma único. A documentação conceitual prevê uma entidade `Family`, mas isso é apenas planejado.

### Observações de integridade

- A validação integral ocorre ao construir/carregar `PedigreeProject`.
- Comandos alteram listas Pydantic por `append`/substituição; mutações internas de listas não reexecutam automaticamente todos os validadores do projeto. A UI atual evita referências ausentes, mas serviços futuros não devem depender apenas da validação de atribuição.
- Existe `schema_version`, mas não há registry de versões nem mecanismo de migração.

## 6. Persistência, importação e exportação

| Operação | Formato | Estado real |
|---|---|---|
| Salvar/abrir | JSON nativo, extensão sugerida `.rps.json` | implementado |
| Importar JSON externo genérico | — | não implementado; somente o schema nativo é aceito |
| Importar PED/FAM | — | não implementado |
| Importar VCF | — | não implementado |
| Importar Phenopacket/GA4GH | — | não implementado |
| Exportar figura | SVG | implementado |
| Exportar figura | PNG, escala 2× | implementado |
| Exportar figura | PDF, 300 dpi | implementado |
| Exportar dados | Phenopacket/PED/FAM/JSON anonimizado | não implementado |

`JsonProjectRepository` limita arquivos carregados a 20 MiB, valida via Pydantic e não executa conteúdo. A gravação usa arquivo temporário no mesmo diretório, `flush`, `fsync`, permissão `0600` e `os.replace`, oferecendo substituição atômica no mesmo filesystem. O limite de 20 MiB é aplicado na leitura, não na gravação. Não existem criptografia, assinatura, checksum, bloqueio concorrente, backup rotativo ou migração de schema.

## 7. Testes automatizados e resultados

Foram coletados oito testes em seis arquivos:

| Arquivo | Teste(s) | Cobertura verificada |
|---|---:|---|
| `test_architecture.py` | 1 | domínio não importa PySide6, SQLite, UI ou persistence |
| `test_domain_states.py` | 2 | unknown ≠ absent; motivos de ausência permanecem distintos |
| `test_json_repository.py` | 1 | round-trip JSON, UUID/indivíduos e permissão privada |
| `test_main_window.py` | 1 | adicionar pessoa, undo e redo sincronizam projeto/cena |
| `test_models.py` | 2 | relação com membro ausente é rejeitada; round-trip preserva unknown |
| `test_rendering.py` | 1 | cena básica e arquivos SVG/PNG/PDF com assinaturas válidas |

Resultado reexecutado:

```text
8 passed in 0.14s
```

O Ruff também foi reexecutado e passou. Não há configuração/relatório de cobertura, testes de integração completos, testes de migração, testes de entradas hostis, testes de carga, acessibilidade, golden images, persistência via UI, relações consanguíneas ou interação real de mouse/teclado. O documento `tests/TRACEABILITY.md` é um plano, não evidência de execução das regras ali listadas.

## 8. Pendências e limitações conhecidas

### Prioridade alta antes de dados clínicos

1. Definir licença do projeto.
2. Criar migrações para `schema_version` antes de ampliar o JSON.
3. Implementar família, parentagem biológica/social/gestacional e eventos reprodutivos.
4. Implementar proveniência, consentimento de exibição e estados `unknown/not_tested/not_asked/withheld` nos modelos clínicos reais.
5. Adicionar fechamento seguro: aviso de alterações não salvas antes de novo/abrir/sair.
6. Implementar exclusão consistente e regras de cascata/rejeição.
7. Definir threat model, backup e futura criptografia; `0600` não equivale a criptografia.

### Limitações do protótipo

- Somente pessoas e parcerias; sem estrutura multigeracional.
- Nenhuma análise genética ou clínica.
- Sem legenda científica e sem símbolos avançados.
- Sem auto-layout/alinhamento.
- Sem SQLite ou persistência de preferências.
- Sem importadores ou relatório de perda de dados.
- Sem anonimização de exportação; figuras podem conter rótulos informados pelo usuário.
- Sem telemetria por ausência de código correspondente, mas também sem política técnica automatizada que impeça futuras chamadas de rede.
- `platformdirs` está instalado, porém não utilizado.
- Módulos `genetics`, `terminology`, `interchange`, `privacy` e `rules` não possuem classes ou serviços.

## 9. Compatibilidade com HPO, HGVS, VCF e segregação

### Pontos favoráveis

- O domínio não depende de Qt ou persistência, verificado por teste arquitetural.
- UUIDs fornecem referências estáveis para observações, genótipos e relações futuras.
- Pydantic facilita schemas versionados, validação e JSON.
- `rendering` recebe objetos do domínio, permitindo acrescentar dados sem substituir `QGraphicsScene`/`QGraphicsView`.
- Diretórios dedicados já existem para `terminology`, `genetics`, `interchange` e `rules`.
- O formato nativo possui `schema_version`, que pode sustentar migrações se o mecanismo for criado agora.

### Lacunas específicas

**HPO:** compatibilidade arquitetural boa, implementação inexistente. São necessários `PhenotypicObservation`, estado presente/ausente/desconhecido, onset/resolution, versão da ontologia, proveniência e um provider/cache offline. `phenotype_status` atual é global por pessoa e insuficiente para múltiplos fenótipos.

**HGVS:** compatibilidade conceitual boa, implementação inexistente. Variantes devem ser entidades separadas com valor original, valor normalizado, sequência/transcrito de referência, assembly e versão HGVS. Nenhuma biblioteca de parsing/normalização HGVS está instalada.

**VCF:** deve entrar como adaptador em `interchange`, não diretamente no domínio ou na UI. Não há `pysam`, `cyvcf2` ou parser equivalente. Será necessário vincular amostras VCF a indivíduos, preservar cabeçalho/assembly, limitar tamanho, tratar genótipos ausentes/fase e produzir relatório de importação. O JSON atual não comporta amostras ou genótipos.

**Segregação:** a arquitetura comporta um serviço puro em `genetics`/`rules`, mas o modelo atual não possui relações parentais, variantes, genótipos, fase, penetrância, fenocópias ou evidência. Portanto, integração não exige reescrever canvas/persistência, mas exige ampliar substancialmente o domínio antes de qualquer algoritmo válido.

### Acoplamento a observar

Os comandos da camada `application` importam diretamente classes Qt (`QUndoCommand`) e tipos de `rendering`. Isso é aceitável no protótipo, porém casos de uso genéticos da Fase 5 devem ser serviços Python puros; apenas adaptadores de UI devem envolvê-los em comandos Qt. Assim evita-se levar Qt para pipelines de importação, testes e análise de segregação.

## 10. Recomendações para iniciar a Fase 5 sem reescrita

### Sequência recomendada

1. **Congelar o contrato 0.1.0.** Criar fixtures JSON do schema atual e testes de compatibilidade. Implementar um `SchemaMigrator` antes de alterar `PedigreeProject`.
2. **Adicionar modelos por composição.** Criar novos arquivos no domínio (`phenotypes.py`, `variants.py`, `families.py`, `provenance.py`) e referenciá-los por UUID. Não inserir HPO/VCF dentro de `IndividualItem`.
3. **Introduzir `Family` sem quebrar arquivos existentes.** Migrar projetos 0.1.0 para uma família padrão e preservar `project_id`, `Individual.id` e `Relationship.id`.
4. **Generalizar relações de modo compatível.** Manter os dois valores existentes de `RelationshipKind` e acrescentar parentagem/adoção/gestação por novas entidades ou arestas tipadas. Não reinterpretar silenciosamente `member_a/member_b`.
5. **Criar interfaces de terminologia.** `HpoProvider` deve expor versão, busca e resolução local; uma implementação cacheada pode usar `platformdirs`. O domínio armazena IDs e versão, nunca objetos Qt.
6. **Modelar fenótipo antes da UI HPO.** Suportar múltiplas observações por pessoa e negação explícita. Depois, adaptar o painel de propriedades com uma aba/lista, mantendo os campos atuais durante a migração.
7. **Modelar variante/genótipo antes do VCF.** Separar `Variant`, `Sample`, `GenotypeObservation`, `VariantInterpretation` e `SegregationEvidence`. Armazenar original + normalizado e proveniência.
8. **Implementar VCF como importador transacional.** O adaptador produz DTOs e relatório de warnings/perdas; um caso de uso valida tudo antes de alterar o projeto. Importação deve ser cancelável e não bloquear a UI.
9. **Criar motor de regras explicável.** Cada resultado deve carregar ID `PED-*`/critério, severidade, entidades envolvidas, fonte e mensagem. Não transformar inferência em diagnóstico.
10. **Manter o renderizador atual.** Acrescentar overlays/anotações e legenda por projeções de dados; não fazer `IndividualItem` consultar HPO, VCF ou banco diretamente.
11. **Adicionar uma porta de repositório.** Fazer UI depender de uma interface `ProjectRepository`; manter `JsonProjectRepository` e, depois, adicionar SQLite como outro adaptador. Isso evita reescrever a janela.
12. **Expandir testes antes dos widgets.** Fixtures sintéticas para HPO, variantes e trios; round-trip/migração; VCF mínimo; fase cis/trans; unknown versus negative; segregação explicada; golden SVG somente para símbolos confirmados.

### Critério de entrada recomendado para a UI da Fase 5

Antes de expor HPO/variantes no editor, devem existir: schema migrável, modelos puros validados, fixtures sintéticas, importadores com relatório e testes de round-trip. Cumprido isso, a UI atual pode receber painéis adicionais sem alteração estrutural de `PedigreeScene`, `PedigreeView`, exportadores ou comandos básicos já funcionais.

## Conclusão

A Fase 4 entregou um núcleo gráfico pequeno, testado e utilizável como base de desenvolvimento, mas não ainda um sistema completo de heredogramas clínicos. A separação domínio/renderização e o uso de UUID/Pydantic são adequados à Fase 5. O caminho de menor risco é ampliar o domínio e os adaptadores de forma versionada, mantendo o editor como consumidor de projeções, em vez de incorporar terminologias e genômica diretamente nos itens Qt.
