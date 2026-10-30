import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

Dialog {
    id: root
    objectName: "nexusPreferences"
    property var controller
    property var trFn
    parent: Overlay.overlay
    width: 600; height: 470; modal: true
    x: (parent.width - width) / 2; y: (parent.height - height) / 2
    closePolicy: Popup.CloseOnEscape
    background: Rectangle { radius: 14; color: NexusTheme.backgroundSecondary; border.color: NexusTheme.borderSubtle }
    contentItem: ColumnLayout {
        anchors.fill: parent; anchors.margins: 24; spacing: 14
        Text { text: trFn("Preferências"); color: NexusTheme.textPrimary; font.pixelSize: 21; font.bold: true }
        Text { text: trFn("Cores de representação"); color: NexusTheme.accentBlue; font.bold: true }
        RowLayout { Layout.fillWidth: true
            Repeater { model: [{n:"Scientific",m:"#3B82F6",w:"#F472B6",u:"#94A3B8"},{n:"Colorblind",m:"#0072B2",w:"#D55E00",u:"#7A7A7A"},{n:"Contrast",m:"#0057FF",w:"#D00070",u:"#111111"}]
                NexusButton { text: modelData.n; onClicked: { man.text=modelData.m; woman.text=modelData.w; unspecified.text=modelData.u } }
            }
        }
        TextField { id: man; Layout.fillWidth: true; text: "#3B82F6"; placeholderText: "Masculino / square" }
        TextField { id: woman; Layout.fillWidth: true; text: "#F472B6"; placeholderText: "Feminino / circle" }
        TextField { id: unspecified; Layout.fillWidth: true; text: "#94A3B8"; placeholderText: "Não especificado / diamond" }
        CheckBox { id: mono; text: trFn("Modo científico monocromático") }
        RowLayout { Layout.fillWidth: true
            Repeater { model: [man.text, woman.text, unspecified.text]
                Rectangle { Layout.fillWidth: true; height: 62; radius: 10; color: NexusTheme.surfacePrimary; border.color: modelData; border.width: 4 }
            }
        }
        Item { Layout.fillHeight: true }
        RowLayout { Layout.alignment: Qt.AlignRight
            NexusButton { text: trFn("Cancelar"); onClicked: root.reject() }
            NexusButton { text: trFn("Confirmar"); primary: true; onClicked: { controller.setColors(man.text,woman.text,unspecified.text,mono.checked); root.accept() } }
        }
    }
}
