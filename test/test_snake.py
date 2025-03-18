import sys
import random
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *


class SnakeGame(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Snake Game')
        self.setGeometry(100, 100, 600, 400)

        self.cell_size = 20
        self.timer_interval = 100
        self.score = 0

        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.food = self.create_food()

        self.timer = QTimer(self)
        self.direction = 'Right'

        self.timer.timeout.connect(self.move_snake)
        self.timer.start(self.timer_interval)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.draw_snake(qp)
        self.draw_food(qp)
        qp.end()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Left and self.direction != 'Right':
            self.direction = 'Left'
        elif key == Qt.Key_Right and self.direction != 'Left':
            self.direction = 'Right'
        elif key == Qt.Key_Up and self.direction != 'Down':
            self.direction = 'Up'
        elif key == Qt.Key_Down and self.direction != 'Up':
            self.direction = 'Down'

    def move_snake(self):
        head_x, head_y = self.snake[0]
        if self.direction == 'Left':
            new_head = (head_x - self.cell_size, head_y)
        elif self.direction == 'Right':
            new_head = (head_x + self.cell_size, head_y)
        elif self.direction == 'Up':
            new_head = (head_x, head_y - self.cell_size)
        elif self.direction == 'Down':
            new_head = (head_x, head_y + self.cell_size)

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 10
            self.food = self.create_food()
        else:
            self.snake.pop()

        self.check_collision()

    def draw_snake(self, qp):
        for x, y in self.snake:
            qp.fillRect(x, y, self.cell_size, self.cell_size,
                        Qt.GlobalColor.green)

    def draw_food(self, qp):
        qp.fillRect(self.food[0], self.food[1], self.cell_size, self.cell_size,
                    Qt.GlobalColor.red)

    def create_food(self):
        x = random.randint(0,
                           self.width() / self.cell_size - 1) * self.cell_size
        y = random.randint(0,
                           self.height() / self.cell_size - 1) * self.cell_size
        return x, y

    def check_collision(self):
        x, y = self.snake[0]
        if x < 0 or x >= self.width() or y < 0 or y >= self.height() or (
                x, y) in self.snake[1:]:
            self.game_over()

    def game_over(self):
        self.timer.stop()
        message = f'Game Over! Your score: {self.score}'
        QMessageBox.information(self, 'Game Over', message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = SnakeGame()
    game.show()
    sys.exit(app.exec())
