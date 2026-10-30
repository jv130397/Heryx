import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

Dialog {
    id: root
    objectName: "personEditor"
    property var controller
    property var trFn
    parent: Overlay.overlay
    width: 520; height: 420; modal: true
    x: (parent.width - width) / 2; y: (parent.height - height) / 2
    closePolicy: Popup.CloseOnEscape
    enter: Transition { NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 160 } }
    background: Rectangle { radius: 14; color: NexusTheme.backgroundSecondary; border.color: NexusTheme.borderSubtle }
    onOpened: {
        nameField.text = controller.selectedPerson.label || ""
        phenotype.currentIndex = controller.selectedPerson.phenotype === "present" ? 1 : controller.selectedPerson.phenotype === "absent" ? 2 : 0
        deceased.checked = controller.selectedPerson.deceased || false
        nameField.forceActiveFocus()
    }
    contentItem: ColumnLayout {
        anchors.fill: parent; anchors.margins: 24; spacing: 16
        RowLayout {
            Layout.fillWidth: true
            ColumnLayout { Layout.fillWidth: true
                Text { text: trFn("Editar indivíduo"); color: NexusTheme.textPrimary; font.pixelSize: 21; font.bold: true }
                Text { text: controller.selectedPerson.id || ""; color: NexusTheme.textSecondary; font.pixelSize: 11 }
            }
            Rectangle { width: 66; height: 66; radius: 12; color: NexusTheme.surfaceElevated; border.color: NexusTheme.accentBlue
                Text { anchors.centerIn: parent; text: controller.selectedPerson.gender === "man" ? "□" : controller.selectedPerson.gender === "woman" ? "○" : "◇"; color: "white"; font.pixelSize: 38 }
            }
        }
        TextField { id: nameField; objectName: "personNameField"; Layout.fillWidth: true; placeholderText: trFn("Identificação"); selectByMouse: true }
        ComboBox { id: phenotype; Layout.fillWidth: true; model: [trFn("Desconhecido"), trFn("Afetado"), trFn("Não afetado")] }
        CheckBox { id: deceased; text: trFn("Falecido") }
        Item { Layout.fillHeight: true }
        RowLayout { Layout.alignment: Qt.AlignRight; spacing: 10
            NexusButton { text: trFn("Cancelar"); onClicked: root.reject() }
            NexusButton { text: trFn("Confirmar"); primary: true; onClicked: {
                var states = ["unknown", "present", "absent"]
                controller.updateSelected(nameField.text, states[phenotype.currentIndex], deceased.checked)
                root.accept()
            } }
        }
    }
}
