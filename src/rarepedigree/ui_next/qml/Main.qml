import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "theme"
import "components"
import "canvas"
import "panels"
import "dialogs"

ApplicationWindow {
    id: window
    objectName: "nexusWindow"
    width: 1440; height: 900; minimumWidth: 1080; minimumHeight: 680
    visible: true; title: "RarePedigree Studio — Genomic Nexus"
    color: NexusTheme.backgroundPrimary
    property bool railExpanded: true
    property int languageRevision: 0
    function tx(source) { languageRevision; return nexus.translate(source) }
    Connections { target: nexus; function onLanguageChanged() { window.languageRevision++ } }

    header: Rectangle {
        height: 76; color: NexusTheme.backgroundPrimary; border.color: NexusTheme.borderSubtle
        RowLayout { anchors.fill: parent; anchors.leftMargin: 22; anchors.rightMargin: 22; spacing: 16
            Rectangle { width: 44; height: 44; radius: 12; gradient: Gradient { GradientStop { position: 0; color: NexusTheme.accentBlue } GradientStop { position: 1; color: NexusTheme.accentViolet } }
                Text { anchors.centerIn: parent; text: "N"; color: "white"; font.bold: true; font.pixelSize: 24 }
            }
            Column { Layout.preferredWidth: 225
                Text { text: "RarePedigree Studio"; color: NexusTheme.textPrimary; font.pixelSize: 17; font.bold: true }
                Text { text: "GENOMIC NEXUS · UI 2.0"; color: NexusTheme.accentBlue; font.pixelSize: 10; font.letterSpacing: 1.2 }
            }
            Rectangle { width: 1; Layout.fillHeight: true; Layout.topMargin: 18; Layout.bottomMargin: 18; color: NexusTheme.borderSubtle }
            Column { Layout.fillWidth: true
                Text { text: nexus.projectName; color: NexusTheme.textPrimary; font.pixelSize: 15; font.bold: true }
                Row { spacing: 7; Rectangle { width: 8; height: 8; radius: 4; color: "#22C55E"; anchors.verticalCenter: parent.verticalCenter }
                    Text { text: tx("Projeto atualizado"); color: NexusTheme.textSecondary; font.pixelSize: 11 }
                }
            }
            NexusButton { text: "↶"; enabled: nexus.canUndo; onClicked: nexus.undo() }
            NexusButton { text: "↷"; enabled: nexus.canRedo; onClicked: nexus.redo() }
            NexusButton { text: "Auto-layout"; enabled: false; ToolTip.visible: hovered; ToolTip.text: "Experimental: layout Python já aplicado" }
            NexusButton { text: tx("Exportar"); enabled: false; ToolTip.visible: hovered; ToolTip.text: "Experimental" }
            NexusButton { text: nexus.language === "en" ? "EN" : "PT"; onClicked: nexus.setLanguage(nexus.language === "en" ? "pt_BR" : "en") }
            NexusButton { text: "⚙"; onClicked: preferences.open() }
        }
    }

    RowLayout {
        anchors.fill: parent; spacing: 0
        Rectangle {
            Layout.preferredWidth: railExpanded ? 214 : 66; Layout.fillHeight: true
            color: NexusTheme.backgroundSecondary; border.color: NexusTheme.borderSubtle
            Behavior on Layout.preferredWidth { NumberAnimation { duration: 170; easing.type: Easing.OutCubic } }
            Column { anchors.fill: parent; anchors.margins: 9; spacing: 6
                ToolItem { compact: !railExpanded; text: railExpanded ? "«  Recolher" : ""; glyph: railExpanded ? "«" : "»"; onClicked: railExpanded = !railExpanded }
                ToolItem { compact: !railExpanded; text: tx("Selecionar"); glyph: "↖"; checked: true }
                ToolItem { compact: !railExpanded; text: tx("Adicionar indivíduo"); glyph: "+○"; enabled: false; ToolTip.visible: hovered; ToolTip.text: "Experimental" }
                ToolItem { compact: !railExpanded; text: tx("Adicionar familiar"); glyph: "○○"; enabled: false }
                ToolItem { compact: !railExpanded; text: tx("Relacionamentos"); glyph: "⌁"; enabled: false }
                ToolItem { compact: !railExpanded; text: tx("Mover"); glyph: "✥"; enabled: false }
                Item { width: 1; height: 12 }
                ToolItem { compact: !railExpanded; text: tx("Excluir"); glyph: "⌫"; enabled: false }
            }
        }
        PedigreeCanvas { id: pedigree; objectName: "pedigreeCanvas"; Layout.fillWidth: true; Layout.fillHeight: true; controller: nexus }
        PropertiesPanel { Layout.preferredWidth: 340; Layout.fillHeight: true; controller: nexus; trFn: window.tx; onEditRequested: editor.open() }
    }

    footer: Rectangle {
        height: 42; color: NexusTheme.backgroundPrimary; border.color: NexusTheme.borderSubtle
        RowLayout { anchors.fill: parent; anchors.leftMargin: 18; anchors.rightMargin: 18
            Text { text: nexus.personCount + " " + tx("indivíduos") + "  ·  " + nexus.generationCount + " " + tx("gerações"); color: NexusTheme.textSecondary }
            Item { Layout.fillWidth: true }
            Text { text: "●  " + tx("Projeto atualizado"); color: "#4ADE80" }
        }
    }
    PersonEditor { id: editor; controller: nexus; trFn: window.tx }
    NexusPreferences { id: preferences; controller: nexus; trFn: window.tx }
}
