import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick 2.0

ApplicationWindow {
    visible: true
    width: 1000
    height: 618
    minimumWidth: 400
    minimumHeight: 300
    title: qsTr("成语接龙")

    ColumnLayout
    {
        anchors.fill: parent
        spacing: 10
        RowLayout {
            Text {
                id: inputText
                // font.pixelSize: 24
                // color: "blue"
                property string strText: "我方"
                text: strText
            }

            TextField {
                id: inputField
                placeholderText: "我方输入"
                Layout.fillWidth: true
                onTextChanged: {
                    // 在这里处理文本内容变化事件
                    console.log("inputField文本内容发生变化：" + text);
                }
            }
        }

        Button {
            text: "提交"
            onClicked: {
                idiom_logic.valid(inputField.text);
            }
        }

        // RowLayout {
        //     anchors.fill: parent
        //     spacing: 10

        //     Text {
        //         id: outputText
        //         // font.pixelSize: 24
        //         // color: "blue"
        //         property string strText: "电脑方"
        //         text: strText
        //     }

        //         TextField {
        //             id: outputField
        //             text: idiom_logic.result
        //             placeholderText: "电脑接龙"
        //             Layout.fillWidth: true
        //             onTextChanged: {
        //                 // 在这里处理文本内容变化事件
        //                 console.log("outputField文本内容发生变化：" + text);
        //             }
        //     }
        // }
    }
}
