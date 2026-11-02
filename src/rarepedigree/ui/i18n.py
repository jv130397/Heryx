"""Qt Linguist-backed application translation and language persistence."""

from pathlib import Path

from PySide6.QtCore import QCoreApplication, QObject, QSettings, QTranslator, Signal

CATALOG = {
    "en": {
        "Novo": "New",
        "Abrir…": "Open…",
        "Salvar": "Save",
        "Salvar como…": "Save as…",
        "Exportar figura…": "Export figure…",
        "Sair": "Quit",
        "Desfazer": "Undo",
        "Refazer": "Redo",
        "Organização automática": "Auto layout",
        "Preferências…": "Preferences…",
        "Selecionar": "Select",
        "Adicionar indivíduo": "Add individual",
        "Adicionar homem/menino": "Add male",
        "Adicionar mulher/menina": "Add female",
        "Adicionar gênero não especificado": "Add unspecified gender",
        "Adicionar familiar": "Add relative",
        "Relacionamento": "Relationship",
        "Relação consanguínea": "Consanguineous relationship",
        "Relação separada": "Separated relationship",
        "Relação divorciada": "Divorced relationship",
        "Mover": "Move",
        "Excluir": "Delete",
        "Ajustar à tela": "Fit to view",
        "Ampliar": "Zoom in",
        "Reduzir": "Zoom out",
        "Sem título": "Untitled",
        "SALVO": "SAVED",
        "NÃO SALVO": "UNSAVED",
        "Propriedades do indivíduo": "Individual properties",
        "Inspector de relações": "Relationship inspector",
        "Selecione uma conexão para inspecionar suas relações.": (
            "Select a connection to inspect its relationships."
        ),
        "Homem/menino": "Male",
        "Mulher/menina": "Female",
        "Gênero diverso": "Gender diverse",
        "Não conhecido/especificado": "Unknown/unspecified",
        "Desconhecido": "Unknown",
        "Clinicamente afetado": "Clinically affected",
        "Explicitamente não afetado": "Explicitly unaffected",
        "Afetado": "Affected",
        "Não afetado": "Unaffected",
        "Estado desconhecido": "Unknown status",
        "Adicionar filho": "Add child",
        "Adicionar pais": "Add parents",
        "Adicionar pai": "Add father",
        "Adicionar mãe": "Add mother",
        "Adicionar parceiro": "Add partner",
        "Adicionar irmão": "Add sibling",
        "Indivíduo adicionado": "Individual added",
        "Indivíduo atualizado": "Individual updated",
        "Exportação concluída": "Export completed",
        "Importar projeto": "Import project",
        "Importar": "Import",
        "Abra um projeto RarePedigree compatível": "Open a compatible RarePedigree project",
        "Selecione um arquivo .rps.json": "Select an .rps.json file",
        "Procurar…": "Browse…",
        "Arquivo": "File",
        "Tela inicial": "Home screen",
        "Genética • Família • Descoberta": "Genetics • Family • Discovery",
        "Privacidade por padrão: seus projetos permanecem neste computador.": (
            "Privacy by default: your projects stay on this computer."
        ),
        "Bem-vindo ao seu espaço científico": "Welcome to your scientific workspace",
        "Crie, documente e explore heredogramas clínicos com clareza.": (
            "Create, document and explore clinical pedigrees with clarity."
        ),
        "Nova família": "New family",
        "Inicie um heredograma com o assistente de projeto.": (
            "Start a pedigree with the project assistant."
        ),
        "Abrir projeto": "Open project",
        "Carregue um arquivo RarePedigree existente.": (
            "Load an existing RarePedigree file."
        ),
        "Projetos recentes": "Recent projects",
        "Retome rapidamente um trabalho local.": "Quickly resume local work.",
        "Nenhum projeto recente": "No recent projects",
        "Limpar lista": "Clear list",
        "Remover da lista": "Remove from list",
        "indisponível": "unavailable",
        "Ilustração científica de heredograma": "Scientific pedigree illustration",
        "O conteúdo será validado antes de substituir o projeto aberto.": (
            "The contents will be validated before replacing the open project."
        ),
        "Arquivo necessário": "File required",
        "Selecione um projeto.": "Select a project.",
        "Exportar heredograma": "Export pedigree",
        "Escolha o formato e a apresentação da figura": (
            "Choose the figure format and presentation"
        ),
        "vetorial": "vector",
        "imagem": "image",
        "documento": "document",
        "Formato": "Format",
        "Destino": "Destination",
        "Incluir legenda científica": "Include scientific legend",
        "Incluir anotações visíveis": "Include visible annotations",
        "Adicionar anotação": "Add annotation",
        "Editar anotação": "Edit annotation",
        "Duplicar anotação": "Duplicate annotation",
        "Excluir anotação": "Delete annotation",
        "Excluir esta anotação?": "Delete this annotation?",
        "Anotação": "Annotation",
        "Comentário visual do usuário": "User visual comment",
        "Tipo": "Type",
        "Título": "Title",
        "Texto": "Text",
        "Observação geral": "General note",
        "Pendência de revisão": "Review pending",
        "Informação a confirmar": "Information to confirm",
        "Comentário técnico": "Technical comment",
        "Identificador manual": "Manual identifier",
        "Numeração genealógica (I-1, II-3)": "Genealogical numbering (I-1, II-3)",
        "Numeração e identificador manual": "Numbering and manual identifier",
        "Rótulo dos indivíduos": "Individual labels",
        "Configurar rótulos…": "Configure labels…",
        "Configurar rótulos": "Configure labels",
        "Escolha como identificar os indivíduos no canvas": (
            "Choose how to identify individuals on the canvas"
        ),
        "Rótulo principal": "Primary label",
        "Mostrar rótulos auxiliares": "Show auxiliary labels",
        "Prévia": "Preview",
        "ações familiares": "family actions",
        "Adicionar ascendentes": "Add ancestors",
        "Adicionar descendente": "Add descendant",
        "Confirmar relação": "Confirm relationship",
        "Adicionar este familiar na posição indicada?": (
            "Add this relative at the indicated position?"
        ),
        "Pessoal": "Personal",
        (
            "Condições, HPO e resultados genéticos serão habilitados "
            "quando o modelo clínico os suportar."
        ): (
            "Conditions, HPO and genetic results will be enabled when supported "
            "by the clinical model."
        ),
        "Descartar alterações?": "Discard changes?",
        "Há alterações não salvas neste indivíduo.": (
            "There are unsaved changes for this individual."
        ),
        "indivíduo": "individual",
        "indivíduos": "individuals",
        "geração": "generation",
        "gerações": "generations",
        "Legenda: preenchido = afetado": "Legend: filled = affected",
        "estado desconhecido": "unknown status",
        "falecido": "deceased",
        "contorno azul/rosa/cinza = categoria de representação": (
            "blue/pink/gray outline = representation category"
        ),
        "modo científico monocromático": "scientific monochrome mode",
        "Identificação": "Identity",
        "Relações": "Relations",
        "Clínica": "Clinical",
        "Editar": "Edit",
        "Exibir": "View",
        "Aplicar": "Apply",
        "Português (Brasil)": "Portuguese (Brazil)",
        "Inglês": "English",
        "Idioma": "Language",
        "Aparência": "Appearance",
        "Heredograma": "Pedigree",
        "Exportação": "Export",
        "Cancelar": "Cancel",
        "Confirmar": "Confirm",
        "Editar indivíduo": "Edit individual",
        "Identificação e representação científica": "Identity and scientific representation",
        "Adicionar irmão ou irmã": "Add brother or sister",
        "Defina explicitamente o núcleo parental compartilhado": (
            "Explicitly define the shared parental unit"
        ),
        "Editar parentesco entre irmãos": "Edit sibling relationship",
        "Revise o impacto antes de confirmar a alteração": (
            "Review the impact before confirming the change"
        ),
        "Novo projeto": "New project",
        "Configure o espaço clínico e científico inicial": (
            "Configure the initial clinical and scientific workspace"
        ),
        "Pais": "Parents",
        "Genitores desconhecidos": "Unknown parents",
        "Irmãos completos": "Full siblings",
        "Meio-irmãos": "Half-siblings",
        "Parceiros": "Partners",
        "Filhos": "Children",
        "Parentesco com o probando": "Relationship to proband",
        "Avisos": "Warnings",
        "nenhum": "none",
        "não registrados": "not registered",
        "não calculado": "not calculated",
        "não determinado": "not determined",
        "nenhuma ambiguidade detectada": "no ambiguity detected",
        "Identificador exibido": "Displayed identifier",
        "Símbolo/gênero": "Symbol/gender",
        "Estado fenotípico": "Phenotype status",
        "Falecido": "Deceased",
        "Preservar posição no auto-layout": "Preserve position in auto layout",
        "Selecione um indivíduo para consultar ou editar suas propriedades.": (
            "Select an individual to inspect or edit its properties."
        ),
        "Projeto salvo": "Project saved",
        "Pronto": "Ready",
        "Salvo": "Saved",
        "Alterado": "Modified",
        "Comece um novo heredograma": "Start a new pedigree",
        "Adicione o primeiro indivíduo para iniciar a construção familiar.": (
            "Add the first individual to begin building the family."
        ),
        "Adicionar primeiro indivíduo": "Add first individual",
        "Zoom para seleção": "Zoom to selection",
        "Restaurar 100%": "Restore 100%",
        "Buscar indivíduo…": "Find individual…",
        "Buscar indivíduo, parentesco ou UUID…": "Search individual, kinship or UUID…",
        "Buscar indivíduos": "Search individuals",
        "Busca de indivíduos": "Individual search",
        "Focar no probando": "Focus on proband",
        "Limpar foco": "Clear focus",
        "Mais opções familiares": "More family options",
        "Visão": "View",
        "Geral": "Overview",
        "Focada": "Focused",
        "Científica": "Scientific",
        "Ramos": "Branches",
        "Ramo materno": "Maternal branch",
        "Ramo paterno": "Paternal branch",
        "Ascendentes": "Ancestors",
        "Descendentes": "Descendants",
        "Irmãos e meio-irmãos": "Siblings and half-siblings",
        "Familiares desconhecidos": "Unknown relatives",
        "Visão geral abaixo do limite de legibilidade; use busca ou foco.": (
            "Overview is below the readability threshold; use search or focus."
        ),
        "Defina um probando para usar o foco.": "Define a proband to use focus.",
        "probando": "proband",
        "genitor": "parent",
        "ascendente": "ancestor",
        "descendente": "descendant",
        "afetado": "affected",
        "não afetado": "unaffected",
        "desconhecido": "unknown",
        "Validação: sem erros": "Validation: no errors",
        "Validação: erros": "Validation: errors",
        "Observação HPO": "HPO observation",
        "Termo obsoleto": "Obsolete term",
        "Substituído por": "Replaced by",
        "Estado": "Status",
        "Presente": "Present",
        "Ausente": "Absent",
        "Não avaliado": "Not evaluated",
        "Idade de início": "Age of onset",
        "Ex.: 4 anos, congênito": "E.g. 4 years, congenital",
        "Gravidade": "Severity",
        "Desconhecida": "Unknown",
        "Leve": "Mild",
        "Moderada": "Moderate",
        "Grave": "Severe",
        "Evolução": "Course",
        "Lateralidade": "Laterality",
        "Frequência/recorrência": "Frequency/recurrence",
        "Fonte clínica": "Clinical source",
        "Data da avaliação": "Assessment date",
        "Comentários": "Comments",
        "Buscar código, nome ou sinônimo HPO…": "Search HPO code, name or synonym…",
        "Busca HPO": "HPO search",
        "Editar observação": "Edit observation",
        "Remover": "Remove",
        "HPO não instalada. Use Preferências para instalar.": (
            "HPO is not installed. Use Preferences to install it."
        ),
        "Nenhum termo encontrado": "No terms found",
        "obsoleto": "obsolete",
        "Registro duplicado": "Duplicate record",
        "Este termo e data já existem.": "This term and date already exist.",
        "Início": "Onset",
        "fenótipos": "phenotypes",
        "presentes": "present",
        "ausentes": "absent",
        "Ontologia HPO": "HPO ontology",
        "Instalar/atualizar HPO oficial": "Install/update official HPO",
        "Versão instalada": "Installed version",
        "Termos": "Terms",
        "Fonte": "Source",
        "Nenhuma versão HPO instalada. O editor continua disponível offline.": (
            "No HPO version is installed. The editor remains available offline."
        ),
        "Baixando e validando fora da interface…": (
            "Downloading and validating outside the UI…"
        ),
        "HPO instalada com sucesso": "HPO installed successfully",
        "Falha na atualização; a base anterior foi preservada.": (
            "Update failed; the previous database was preserved."
        ),
        "Falha na atualização HPO": "HPO update failed",
        "Comparação fenotípica familiar": "Family phenotype comparison",
        "Selecione os indivíduos e compare observações documentadas.": (
            "Select individuals and compare documented observations."
        ),
        "Atualizar matriz": "Refresh matrix",
        "Exportar CSV…": "Export CSV…",
        "Desidentificar identificadores": "De-identify identifiers",
        "Código HPO": "HPO code",
        "Fenótipo": "Phenotype",
        "Exportar matriz": "Export matrix",
        "Todas as gerações": "All generations",
        "Todos os ramos": "All branches",
        "Gerenciar ontologia HPO…": "Manage HPO ontology…",
        (
            "A ontologia é instalada localmente e nenhuma informação clínica "
            "é enviada durante a atualização."
        ): (
            "The ontology is installed locally and no clinical information "
            "is sent during updates."
        ),
        "Comparação fenotípica familiar…": "Family phenotype comparison…",
    }
}


class CatalogTranslator(QTranslator):
    def __init__(self, language: str) -> None:
        super().__init__()
        self.language = language

    def translate(self, context, source_text, disambiguation=None, n=-1):
        del context, disambiguation, n
        return CATALOG.get(self.language, {}).get(source_text, source_text)


class LanguageManager(QObject):
    languageChanged = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.settings = QSettings()
        self.language = self.settings.value("ui/language", "pt_BR", str)
        self.translator: QTranslator | None = None
        self.set_language(self.language, emit=False)

    def set_language(self, language: str, emit: bool = True) -> None:
        language = "en" if language.startswith("en") else "pt_BR"
        app = QCoreApplication.instance()
        if app is not None and self.translator is not None:
            app.removeTranslator(self.translator)
        self.language = language
        translator = QTranslator()
        qm_path = Path(__file__).parents[1] / "translations" / f"rarepedigree_{language}.qm"
        self.translator = (
            translator if translator.load(str(qm_path)) else CatalogTranslator(language)
        )
        if app is not None:
            app.installTranslator(self.translator)
        QSettings().setValue("ui/language", language)
        if emit:
            self.languageChanged.emit(language)

    @property
    def is_first_run(self) -> bool:
        return not QSettings().value("ui/language_selected", False, bool)

    def complete_first_run(self) -> None:
        QSettings().setValue("ui/language_selected", True)


language_manager = LanguageManager()


def tr(text: str) -> str:
    translated = QCoreApplication.translate("RarePedigree", text)
    if translated == text:
        return CATALOG.get(language_manager.language, {}).get(text, text)
    return translated
