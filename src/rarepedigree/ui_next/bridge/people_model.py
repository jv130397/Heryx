"""Read-only QML projection over the Python domain project."""

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt

from rarepedigree.domain import GenderIdentity, PedigreeProject
from rarepedigree.rendering.style import PedigreeRenderStyle


class PeopleModel(QAbstractListModel):
    IdRole = Qt.ItemDataRole.UserRole + 1
    LabelRole = IdRole + 1
    GenderRole = IdRole + 2
    PhenotypeRole = IdRole + 3
    XRole = IdRole + 4
    YRole = IdRole + 5
    DeceasedRole = IdRole + 6
    SelectedRole = IdRole + 7
    OutlineRole = IdRole + 8

    def __init__(self, project: PedigreeProject, style: PedigreeRenderStyle, parent=None) -> None:
        super().__init__(parent)
        self.project = project
        self.style = style
        self.selected_id = ""

    def roleNames(self) -> dict[int, bytes]:
        return {
            self.IdRole: b"personId",
            self.LabelRole: b"label",
            self.GenderRole: b"gender",
            self.PhenotypeRole: b"phenotype",
            self.XRole: b"nodeX",
            self.YRole: b"nodeY",
            self.DeceasedRole: b"deceased",
            self.SelectedRole: b"selected",
            self.OutlineRole: b"outlineColor",
        }

    def rowCount(self, parent=None) -> int:
        parent = parent or QModelIndex()
        return 0 if parent.isValid() else len(self.project.individuals)

    def data(self, index: QModelIndex, role: int):
        if not index.isValid() or not 0 <= index.row() < len(self.project.individuals):
            return None
        person = self.project.individuals[index.row()]
        values = {
            self.IdRole: str(person.id),
            self.LabelRole: person.label,
            self.GenderRole: person.gender_identity.value,
            self.PhenotypeRole: person.phenotype_status.value,
            self.XRole: person.layout.x,
            self.YRole: person.layout.y,
            self.DeceasedRole: person.deceased,
            self.SelectedRole: str(person.id) == self.selected_id,
            self.OutlineRole: self.style.category_color(person.gender_identity),
        }
        return values.get(role)

    def replace_project(self, project: PedigreeProject) -> None:
        self.beginResetModel()
        self.project = project
        self.endResetModel()

    def set_selected(self, person_id: str) -> None:
        self.selected_id = person_id
        if self.rowCount():
            self.dataChanged.emit(
                self.index(0), self.index(self.rowCount() - 1), [self.SelectedRole]
            )

    def refresh(self) -> None:
        if self.rowCount():
            self.dataChanged.emit(self.index(0), self.index(self.rowCount() - 1))

    def person(self, person_id: str):
        return next(person for person in self.project.individuals if str(person.id) == person_id)

    @staticmethod
    def symbol(gender: GenderIdentity) -> str:
        return {GenderIdentity.MAN: "square", GenderIdentity.WOMAN: "circle"}.get(
            gender, "diamond"
        )
