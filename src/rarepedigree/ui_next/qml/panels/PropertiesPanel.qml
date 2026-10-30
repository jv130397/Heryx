import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

Rectangle {
    id: root
    property var controller
    property var trFn
    signal editRequested()
    color: NexusTheme.backgroundSecondary
    border.color: NexusTheme.borderSubtle
    ColumnLayout {
        anchors.fill: parent; anchors.margins: 18; spacing: 14
        Text { text: trFn("Propriedades"); color: NexusTheme.textPrimary; font.pixelSize: 17; font.bold: true }
        Rectangle { Layout.fillWidth: true; height: 132; radius: 12; color: NexusTheme.surfacePrimary; border.color: NexusTheme.borderSubtle
            Column { anchors.centerIn: parent; spacing: 6
                Text { anchors.horizontalCenter: parent.horizontalCenter; text: controller.selectedPerson.gender === "man" ? "□" : controller.selectedPerson.gender === "woman" ? "○" : "◇"; color: NexusTheme.accentBlue; font.pixelSize: 38 }
                Text { anchors.horizontalCenter: parent.horizontalCenter; text: controller.selectedPerson.label || "—"; color: NexusTheme.textPrimary; font.bold: true; font.pixelSize: 16 }
                Text { anchors.horizontalCenter: parent.horizontalCenter; text: controller.selectedPerson.phenotype || ""; color: NexusTheme.textSecondary }
            }
        }
        TabBar { id: tabs; Layout.fillWidth: true
            TabButton { text: trFn("Identificação") }
            TabButton { text: trFn("Relações") }
            TabButton { text: trFn("Clínica") }
        }
        StackLayout { currentIndex: tabs.currentIndex; Layout.fillWidth: true; Layout.fillHeight: true
            ColumnLayout { spacing: 10
                Text { text: trFn("Identificação"); color: NexusTheme.accentBlue; font.bold: true }
                Text { text: controller.selectedPerson.id || ""; color: NexusTheme.textSecondary; wrapMode: Text.WrapAnywhere; Layout.fillWidth: true }
                Text { text: trFn("Fenótipo") + ": " + (controller.selectedPerson.phenotype || "—"); color: NexusTheme.textPrimary }
                Item { Layout.fillHeight: true }
                NexusButton { Layout.fillWidth: true; text: trFn("Editar indivíduo"); primary: true; onClicked: root.editRequested() }
            }
            Text { text: trFn("Relações familiares calculadas pelo núcleo Python."); color: NexusTheme.textSecondary; wrapMode: Text.WordWrap }
            Text { text: trFn("HPO, HGVS e VCF reservados para integração futura."); color: NexusTheme.textSecondary; wrapMode: Text.WordWrap }
        }
    }
}
