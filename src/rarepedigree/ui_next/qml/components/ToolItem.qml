import QtQuick
import QtQuick.Controls
import "../theme"

Button {
    id: root
    property string glyph: "◇"
    property bool compact: false
    checkable: false
    implicitWidth: parent ? parent.width : 190
    implicitHeight: 46
    contentItem: Row {
        spacing: 12
        Text { text: root.glyph; color: root.checked ? "white" : NexusTheme.accentBlue; font.pixelSize: 19; width: 24; horizontalAlignment: Text.AlignHCenter }
        Text { visible: !root.compact; text: root.text; color: NexusTheme.textPrimary; font.pixelSize: 13; anchors.verticalCenter: parent.verticalCenter }
    }
    background: Rectangle {
        radius: 8
        color: root.checked ? "#0F6EB4" : root.hovered ? NexusTheme.surfaceElevated : "transparent"
        border.color: root.checked ? NexusTheme.accentBlue : "transparent"
        Behavior on color { ColorAnimation { duration: 150 } }
    }
}
