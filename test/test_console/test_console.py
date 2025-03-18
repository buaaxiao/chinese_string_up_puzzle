import sys
from PyQt6.QtCore import QProcess
from PyQt6.QtWidgets import QWidget, QApplication, QVBoxLayout, QLineEdit, QTextEdit, QPushButton


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        # 创建 UI
        layout = QVBoxLayout()
        self.command_line_edit = QLineEdit()
        self.output_text_edit = QTextEdit()
        self.exec_button = QPushButton("Execute")
        layout.addWidget(self.command_line_edit)
        layout.addWidget(self.exec_button)
        layout.addWidget(self.output_text_edit)
        self.setLayout(layout)

        # 绑定信号槽
        self.exec_button.clicked.connect(self.execute_command)

    def execute_command(self):
        command = self.command_line_edit.text()

        process = QProcess()

        process.start(command)
        process.waitForStarted()

        process.waitForReadyRead()
        output = process.readAllStandardOutput().data().decode('utf-8')
        print(output)
        self.output_text_edit.append(output.rstrip('\r\n'))

        process.close()


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
