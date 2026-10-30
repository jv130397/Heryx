"""Generate reproducible real-widget screenshots for the Phase 4.6 report."""

from pathlib import Path

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QApplication, QMenu

from rarepedigree.domain import GenderIdentity
from rarepedigree.rendering.exporters import export_png
from rarepedigree.ui import MainWindow

OUTPUT = Path("specifications/assets/phase_4_6")


def save_window(window: MainWindow, name: str) -> None:
    QApplication.processEvents()
    window.grab().save(str(OUTPUT / name))


def family_window() -> tuple[MainWindow, object]:
    window = MainWindow()
    root = window.add_person(GenderIdentity.WOMAN)
    window._context_action(window.scene.person_items[root.id], "parents")
    window._context_action(window.scene.person_items[root.id], "partner")
    partner = next(
        person for person in window.project.individuals if person.id not in {
            root.id, *(edge.parent_id for edge in window.project.parentages)
        }
    )
    window.scene.clearSelection()
    window.scene.person_items[root.id].setSelected(True)
    window.scene.person_items[partner.id].setSelected(True)
    window._context_action(window.scene.person_items[root.id], "child")
    child = window.project.individuals[-1]
    window._context_action(window.scene.person_items[child.id], "child")
    window.auto_layout(push_undo=False)
    window.resize(1600, 900)
    window.show()
    window.fit_pedigree()
    return window, root


def main() -> None:
    app = QApplication.instance() or QApplication([])
    app.setOrganizationName("RarePedigree")
    app.setApplicationName("RarePedigree Studio")
    OUTPUT.mkdir(parents=True, exist_ok=True)

    empty = MainWindow()
    empty.resize(1600, 900)
    empty.show()
    save_window(empty, "01_empty_workspace.png")
    empty.close()

    window, root = family_window()
    window.scene.clearSelection()
    save_window(window, "02_three_generations.png")

    window.scene.person_items[root.id].setSelected(True)
    save_window(window, "03_selected_properties.png")

    menu = QMenu(window)
    for title in (
        "Adicionar pais", "Adicionar parceiro", "Adicionar filho",
        "Adicionar irmão", "Editar propriedades", "Excluir indivíduo",
    ):
        menu.addAction(title)
    menu.ensurePolished()
    menu.resize(menu.sizeHint())
    menu_image = menu.grab()
    window_image = window.grab()
    combined = QImage(window_image.size(), QImage.Format.Format_ARGB32)
    combined.fill(Qt.GlobalColor.transparent)
    painter = QPainter(combined)
    painter.drawPixmap(0, 0, window_image)
    painter.drawPixmap(QPoint(520, 330), menu_image)
    painter.end()
    combined.save(str(OUTPUT / "04_context_menu.png"))

    window.resize(1366, 768)
    window.fit_pedigree()
    save_window(window, "05_reduced_1366x768.png")
    export_png(window.scene, OUTPUT / "06_scientific_export.png")
    window.undo_stack.setClean()
    window.close()


if __name__ == "__main__":
    main()
