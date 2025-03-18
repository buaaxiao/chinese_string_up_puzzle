import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


class ChessPiece(QLabel):

    def __init__(self, parent, piece_type, x, y):
        super().__init__(parent)
        self.piece_type = piece_type
        self.x = x
        self.y = y
        self.setGeometry(x * 50, y * 50, 50, 50)
        self.setPixmap(QPixmap(f'images/{piece_type}.png').scaled(50, 50))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent().start_drag_piece(self)

    def move_to(self, x, y):
        self.x = x
        self.y = y
        self.setGeometry(x * 50, y * 50, 50, 50)


class ChessBoard(QWidget):

    def __init__(self):
        super().__init__()

        self.init_ui()
        self.init_pieces()

    def init_pieces(self):
        self.pieces = []

        # 黑方棋子
        self.pieces.append(ChessPiece(self, 'black_rook', 0, 0))
        self.pieces.append(ChessPiece(self, 'black_knight', 1, 0))
        self.pieces.append(ChessPiece(self, 'black_bishop', 2, 0))
        self.pieces.append(ChessPiece(self, 'black_queen', 3, 0))
        self.pieces.append(ChessPiece(self, 'black_king', 4, 0))
        self.pieces.append(ChessPiece(self, 'black_bishop', 5, 0))
        self.pieces.append(ChessPiece(self, 'black_knight', 6, 0))
        self.pieces.append(ChessPiece(self, 'black_rook', 7, 0))
        self.pieces.append(ChessPiece(self, 'black_pawn', 0, 1))
        self.pieces.append(ChessPiece(self, 'black_pawn', 1, 1))
        self.pieces.append(ChessPiece(self, 'black_pawn', 2, 1))
        self.pieces.append(ChessPiece(self, 'black_pawn', 3, 1))
        self.pieces.append(ChessPiece(self, 'black_pawn', 4, 1))
        self.pieces.append(ChessPiece(self, 'black_pawn', 5, 1))
        self.pieces.append(ChessPiece(self, 'black_pawn', 6, 1))
        self.pieces.append(ChessPiece(self, 'black_pawn', 7, 1))

        # 红方棋子
        self.pieces.append(ChessPiece(self, 'red_rook', 0, 9))
        self.pieces.append(ChessPiece(self, 'red_knight', 1, 9))
        self.pieces.append(ChessPiece(self, 'red_bishop', 2, 9))
        self.pieces.append(ChessPiece(self, 'red_queen', 3, 9))
        self.pieces.append(ChessPiece(self, 'red_king', 4, 9))
        self.pieces.append(ChessPiece(self, 'red_bishop', 5, 9))
        self.pieces.append(ChessPiece(self, 'red_knight', 6, 9))
        self.pieces.append(ChessPiece(self, 'red_rook', 7, 9))
        self.pieces.append(ChessPiece(self, 'red_pawn', 0, 8))
        self.pieces.append(ChessPiece(self, 'red_pawn', 1, 8))
        self.pieces.append(ChessPiece(self, 'red_pawn', 2, 8))
        self.pieces.append(ChessPiece(self, 'red_pawn', 3, 8))
        self.pieces.append(ChessPiece(self, 'red_pawn', 4, 8))
        self.pieces.append(ChessPiece(self, 'red_pawn', 5, 8))
        self.pieces.append(ChessPiece(self, 'red_pawn', 6, 8))
        self.pieces.append(ChessPiece(self, 'red_pawn', 7, 8))

    def init_ui(self):
        self.setWindowTitle('Chinese Chess')
        self.setGeometry(100, 100, 500, 550)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        pen = QPen(Qt.GlobalColor.black, 2)
        qp.setPen(pen)

        # 绘制棋盘
        for i in range(10):
            qp.drawLine(0, i * 50, 8 * 50, i * 50)
        for i in range(9):
            if i == 0 or i == 8:
                qp.drawLine(i * 50, 0, i * 50, 9 * 50)
            else:
                qp.drawLine(i * 50, 0, i * 50, 4 * 50)
                qp.drawLine(i * 50, 5 * 50, i * 50, 9 * 50)

        qp.end()

    def start_drag_piece(self, piece):
        self.dragging_piece = piece
        self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self.dragging_piece:
            x = event.x() // 50
            y = event.y() // 50
            if x < 0:
                x = 0
            elif x > 7:
                x = 7
            if y < 0:
                y = 0
            elif y > 9:
                y = 9
            self.dragging_piece.move_to(x, y)

    def mouseReleaseEvent(self, event):
        if self.dragging_piece:
            self.setCursor(Qt.ArrowCursor)
            self.dragging_piece = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    board = ChessBoard()
    board.show()
    sys.exit(app.exec())
