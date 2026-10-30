import QtQuick
import QtQuick.Controls
import "../theme"

Button {
    id: control
    property bool primary: false
    implicitHeight: 40
    leftPadding: 14; rightPadding: 14
    contentItem: Text {
        text: control.text; color: NexusTheme.textPrimary
        font.family: "Inter, Noto Sans"; font.pixelSize: 13; font.weight: Font.Medium
        horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
    }
    background: Rectangle {
        radius: NexusTheme.radius
        color: control.down ? "#164E63" : control.primary ? NexusTheme.accentViolet
              : control.hovered ? NexusTheme.surfaceElevated : NexusTheme.surfacePrimary
        border.color: control.activeFocus ? NexusTheme.accentBlue : NexusTheme.borderSubtle
        Behavior on color { ColorAnimation { duration: NexusTheme.motionFast } }
    }
}
