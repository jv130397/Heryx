"""Generate the mandatory real-widget visual evidence for Phase 4.7."""

from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QTabWidget

from rarepedigree.domain import GenderIdentity, ObservationStatus
from rarepedigree.rendering.exporters import ExportOptions, export_png
from rarepedigree.ui import MainWindow
from rarepedigree.ui.dialogs import EditIndividualDialog
from rarepedigree.ui.i18n import language_manager
from rarepedigree.ui.preferences import PreferencesDialog
from rarepedigree.ui.startup import WelcomeDialog

OUTPUT = Path("specifications/assets/phase_4_7")


def save(widget, name: str) -> None:
    QApplication.processEvents()
    widget.grab().save(str(OUTPUT / name))


def family_window(size=(1600, 900)):
    window = MainWindow()
    root = window.add_person(GenderIdentity.WOMAN)
    root.phenotype_status = ObservationStatus.PRESENT
    window.scene.person_items[root.id].refresh()
    window._context_action(window.scene.person_items[root.id], "parents")
    window._context_action(window.scene.person_items[root.id], "partner")
    window._context_action(window.scene.person_items[root.id], "child")
    child = window.project.individuals[-1]
    window._context_action(window.scene.person_items[child.id], "child")
    window.auto_layout(push_undo=False)
    window.resize(*size)
    window.show()
    window.scene.clearSelection()
    window.scene.person_items[root.id].setSelected(True)
    window.fit_pedigree()
    return window, root


def main() -> None:
    app = QApplication.instance() or QApplication([])
    app.setOrganizationName("RarePedigree")
    app.setApplicationName("RarePedigree Studio")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    settings = QSettings()
    settings.setValue("pedigree/category_colors", True)
    settings.setValue("pedigree/monochrome", False)
    settings.setValue("pedigree/show_legend", True)

    welcome = WelcomeDialog()
    welcome.show()
    save(welcome, "01_language_welcome.png")
    welcome.close()

    language_manager.set_language("pt_BR")
    window, root = family_window()
    save(window, "02_workspace_pt_br.png")

    language_manager.set_language("en")
    window.toast.hide()
    save(window, "03_workspace_en.png")
    language_manager.set_language("pt_BR")
    save(window, "04_configurable_colors.png")

    editor = EditIndividualDialog(root, window)
    editor.show()
    save(editor, "05_edit_individual.png")
    editor.close()

    item = window.scene.person_items[root.id]
    menu, _ = item.build_context_menu()
    popup_position = window.mapToGlobal(window.rect().center())
    menu.popup(popup_position)
    QApplication.processEvents()
    screen = window.screen()
    screen.grabWindow(0).save(str(OUTPUT / "06_context_menu.png"))
    menu.close()

    preferences = PreferencesDialog(window)
    tabs = preferences.findChild(QTabWidget)
    tabs.setCurrentIndex(2)
    preferences.show()
    save(preferences, "07_color_preferences.png")
    preferences.close()

    settings.setValue("pedigree/monochrome", True)
    window.apply_preferences()
    save(window, "08_scientific_monochrome.png")
    export_png(
        window.scene,
        OUTPUT / "09_scientific_export.png",
        ExportOptions(monochrome=True, include_legend=True),
    )

    settings.setValue("pedigree/monochrome", False)
    window.apply_preferences()
    window.resize(1366, 768)
    window.fit_pedigree()
    save(window, "10_workspace_1366x768.png")
    window.resize(1920, 1080)
    window.fit_pedigree()
    save(window, "11_workspace_1920x1080.png")
    window.undo_stack.setClean()
    window.close()


if __name__ == "__main__":
    main()
