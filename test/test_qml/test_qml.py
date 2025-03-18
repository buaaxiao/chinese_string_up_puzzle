import sys
from PyQt6.QtCore import QObject, QUrl, pyqtSignal, pyqtSlot, pyqtProperty
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine


class IdiomLogic(QObject):
    resultChanged = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._result = ""

    @pyqtProperty(str, notify=resultChanged)
    def result(self):
        return self._result

    @pyqtSlot(str)
    def valid(self, idiom):
        self._result = idiom
        self.resultChanged.emit(self._result)


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    app.aboutToQuit.connect(engine.deleteLater)

    idiom_logic = IdiomLogic()
    engine.rootContext().setContextProperty("idiom_logic", idiom_logic)
    engine.load(QUrl.fromLocalFile("idiom.qml"))

    sys.exit(app.exec())
