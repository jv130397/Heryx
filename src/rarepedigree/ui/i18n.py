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
        "Adicionar familiar": "Add relative",
        "Relacionamento": "Relationship",
        "Mover": "Move",
        "Excluir": "Delete",
        "Ajustar à tela": "Fit to view",
        "Sem título": "Untitled",
        "SALVO": "SAVED",
        "NÃO SALVO": "UNSAVED",
        "Propriedades do indivíduo": "Individual properties",
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
    return QCoreApplication.translate("RarePedigree", text)
