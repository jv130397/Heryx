import QtQuick
import QtQuick.Controls
import "../theme"

Item {
    id: root
    property string personId
    property string personLabel
    property string gender
    property string phenotype
    property color outlineColor
    property bool selected: false
    property bool deceased: false
    signal activated(string personId)
    signal contextRequested(string personId, real px, real py)
    width: 76; height: 88

    Rectangle {
        id: halo
        anchors.horizontalCenter: parent.horizontalCenter
        width: 60; height: 60; radius: 12
        color: "transparent"; border.width: root.selected ? 3 : 0
        border.color: NexusTheme.accentBlue
        scale: root.selected ? 1 : 0.86; opacity: root.selected ? 0.36 : 0
        Behavior on scale { NumberAnimation { duration: 160; easing.type: Easing.OutCubic } }
        Behavior on opacity { NumberAnimation { duration: 140 } }
    }
    Canvas {
        id: symbol
        anchors.horizontalCenter: parent.horizontalCenter
        width: 54; height: 54
        onPaint: {
            var p = getContext("2d"); p.reset(); p.lineWidth = root.selected ? 4 : 3;
            p.strokeStyle = root.selected ? NexusTheme.accentBlue : root.outlineColor;
            p.fillStyle = root.phenotype === "present" ? "#202936" : "#FFFFFF";
            p.beginPath();
            if (root.gender === "man") p.rect(7, 7, 40, 40);
            else if (root.gender === "woman") p.arc(27, 27, 20, 0, Math.PI * 2);
            else { p.moveTo(27, 5); p.lineTo(49, 27); p.lineTo(27, 49); p.lineTo(5, 27); p.closePath(); }
            p.fill(); p.stroke();
            if (root.phenotype === "unknown") { p.fillStyle = "#334155"; p.font = "bold 17px sans-serif"; p.textAlign = "center"; p.fillText("?", 27, 33); }
            if (root.deceased) { p.beginPath(); p.moveTo(4, 50); p.lineTo(50, 4); p.stroke(); }
        }
        Connections { target: root; function onSelectedChanged() { symbol.requestPaint() } function onPhenotypeChanged() { symbol.requestPaint() } }
    }
    Text { anchors.top: symbol.bottom; anchors.horizontalCenter: parent.horizontalCenter; text: root.personLabel; color: "#27364B"; font.pixelSize: 12; font.weight: root.selected ? Font.Bold : Font.Normal }
    TapHandler { acceptedButtons: Qt.LeftButton; onTapped: root.activated(root.personId) }
    TapHandler { acceptedButtons: Qt.RightButton; onTapped: point => root.contextRequested(root.personId, point.position.x, point.position.y) }
    HoverHandler { cursorShape: Qt.PointingHandCursor }
}
