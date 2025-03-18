import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


class ChessBoard(QWidget):

    def __init__(self):
        super().__init__()

        self.board = [[0] * 15 for _ in range(15)]  # 棋盘，0表示空，1表示黑子，2表示白子
        self.current_player = 1  # 当前玩家，1表示黑方，2表示白方
        self.game_over = False

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Five in a Row')
        self.setGeometry(100, 100, 600, 600)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        pen = QPen(Qt.GlobalColor.darkGray, 2)
        qp.setPen(pen)

        for i in range(15):
            qp.drawLine(50, 50 + i * 40, 570, 50 + i * 40)
            qp.drawLine(50 + i * 40, 50, 50 + i * 40, 570)

        for i in range(15):
            for j in range(15):
                if self.board[i][j] == 1:
                    qp.setBrush(QBrush(Qt.GlobalColor.black))
                    qp.drawEllipse(45 + i * 40, 45 + j * 40, 30, 30)
                elif self.board[i][j] == 2:
                    qp.setBrush(QBrush(Qt.GlobalColor.white))
                    qp.drawEllipse(45 + i * 40, 45 + j * 40, 30, 30)

        qp.end()

    # def mousePressEvent(self, event):
    #     if self.game_over:
    #         return

    #     x = event.x()
    #     y = event.y()
    #     if x < 50 or x > 570 or y < 50 or y > 570:
    #         return

    #     row = (x - 50) // 40
    #     col = (y - 50) // 40

    #     if self.board[row][col] != 0:
    #         return

    #     self.board[row][col] = self.current_player
    #     self.update()

    #     if self.check_winner(row, col):
    #         self.game_over = True
    #         winner = 'Black' if self.current_player == 1 else 'White'
    #         QMessageBox.information(self, 'Game Over', f'{winner} wins!')

    #     self.current_player = 2 if self.current_player == 1 else 1

    def check_winner(self, row, col):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # 水平、垂直、对角线方向

        for d in directions:
            count = 1
            dx, dy = d
            x, y = row, col

            while count < 5:
                x += dx
                y += dy

                if x < 0 or x >= 15 or y < 0 or y >= 15 or self.board[x][
                        y] != self.current_player:
                    break

                count += 1

            x, y = row, col

            while count < 5:
                x -= dx
                y -= dy

                if x < 0 or x >= 15 or y < 0 or y >= 15 or self.board[x][
                        y] != self.current_player:
                    break

                count += 1

            if count >= 5:
                return True

        return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    board = ChessBoard()
    board.show()
    sys.exit(app.exec())
