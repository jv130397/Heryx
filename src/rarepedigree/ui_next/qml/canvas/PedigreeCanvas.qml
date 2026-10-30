import QtQuick
import QtQuick.Controls
import "../theme"

Rectangle {
    id: root
    property var controller
    property real zoom: 1.0
    color: NexusTheme.canvasBackground
    clip: true

    Canvas {
        anchors.fill: parent
        onPaint: {
            var p = getContext("2d"); p.reset(); p.strokeStyle = "#E4ECF7"; p.lineWidth = 1;
            for (var x = 0; x < width; x += 32) { p.beginPath(); p.moveTo(x, 0); p.lineTo(x, height); p.stroke(); }
            for (var y = 0; y < height; y += 32) { p.beginPath(); p.moveTo(0, y); p.lineTo(width, y); p.stroke(); }
        }
    }
    Flickable {
        id: flick
        anchors.fill: parent; clip: true
        contentWidth: 1500 * root.zoom; contentHeight: 1000 * root.zoom
        boundsBehavior: Flickable.StopAtBounds
        Item {
            id: world
            width: 1500; height: 1000; scale: root.zoom
            transformOrigin: Item.TopLeft
            Canvas {
                id: edges
                anchors.fill: parent
                onPaint: {
                    var p = getContext("2d"); p.reset(); p.strokeStyle = "#35445A"; p.lineWidth = 2;
                    var lines = root.controller.connectors;
                    for (var i = 0; i < lines.length; i++) {
                        var e = lines[i]; var x1 = 500 + e.x1; var y1 = 170 + e.y1;
                        var x2 = 500 + e.x2; var y2 = 170 + e.y2;
                        p.beginPath(); p.moveTo(x1, y1); p.lineTo(x1, (y1+y2)/2); p.lineTo(x2, (y1+y2)/2); p.lineTo(x2, y2); p.stroke();
                    }
                }
            }
            Repeater {
                model: root.controller.peopleModel
                delegate: PersonNode {
                    x: 500 + nodeX - width/2; y: 170 + nodeY - height/2
                    personId: model.personId; personLabel: model.label; gender: model.gender
                    phenotype: model.phenotype; deceased: model.deceased
                    selected: model.selected; outlineColor: model.outlineColor
                    onActivated: id => root.controller.selectPerson(id)
                    onContextRequested: (id, px, py) => { root.controller.selectPerson(id); contextMenu.popup() }
                }
            }
        }
    }
    Rectangle {
        anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 16
        width: 178; height: 44; radius: 10; color: NexusTheme.backgroundSecondary
        Row { anchors.centerIn: parent; spacing: 12
            ToolButton { text: "−"; onClicked: root.zoom = Math.max(.55, root.zoom - .1) }
            Text { text: Math.round(root.zoom*100) + "%"; color: "white"; anchors.verticalCenter: parent.verticalCenter }
            ToolButton { text: "+"; onClicked: root.zoom = Math.min(1.8, root.zoom + .1) }
            ToolButton { text: "⤢"; onClicked: root.zoom = 1 }
        }
    }
    WheelHandler { onWheel: event => { root.zoom = Math.max(.55, Math.min(1.8, root.zoom + event.angleDelta.y/1200)); event.accepted = true } }
    Menu {
        id: contextMenu; objectName: "nexusContextMenu"
        MenuItem { text: qsTr("Editar indivíduo"); enabled: false }
        MenuItem { text: qsTr("Adicionar familiar"); enabled: false }
        MenuSeparator {}
        MenuItem { text: qsTr("Abrir propriedades"); onTriggered: {} }
    }
}
