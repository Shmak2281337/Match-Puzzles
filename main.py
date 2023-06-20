import copy
from puzzle_ui import Ui_MainWindow
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsDropShadowEffect, QMessageBox, QPushButton
from levels import getLevelData

# Константы
x = 4
y = 5
levels_count = 18
key_h = 'horizontal_sticks'
key_v = 'vertical_sticks'
style_hide = 'background: rgba(0,0,0,0);'
style_opacity = 'background: rgba(0,0,0,10);'


class MainWindow(QMainWindow, Ui_MainWindow):
    current_level = 1
    current_level_data = {}
    last_select = []

    def reset(self):
        self.last_select = []

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # нажатия на кнопки и спички
        self.button_back.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(3))
        self.button_answer.clicked.connect(self.answerClick)
        self.button_reset.clicked.connect(lambda: self.startLevel(self.current_level))
        self.button_play.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(3))
        self.button_rules.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.back_levels.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.back_rules.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.button_exit.clicked.connect(lambda: sys.exit())
        for lvl in range(1, levels_count+1):
            getattr(self, 'button_level_%s' % lvl).pressed.connect(lambda start_level=lvl: self.startLevel(start_level))
        for i in range(y+1):
            for j in range(x):
                getattr(self, 'button_h%s' % (str(i)+str(j))).pressed.connect(lambda select=[key_h, i, j]: self.moving(select))
        for i in range(y):
            for j in range(x+1):
                getattr(self, 'button_v%s' % (str(i)+str(j))).pressed.connect(lambda select=[key_v, i, j]: self.moving(select))

    def startLevel(self, start_level):
        self.current_level = start_level
        self.reset()
        self.current_level_data = getLevelData(start_level)
        self.stackedWidget.setCurrentIndex(0)
        # отрисовка интерфейса
        self.drawField()
        self.label_task.setText(self.current_level_data.get('task'))

    def answerClick(self):
        answer = copy.deepcopy(self.current_level_data['answer'])
        self.current_level_data[key_h] = answer[key_h]
        self.current_level_data[key_v] = answer[key_v]
        self.drawField()
        self.alertWin()

    def differences(self):
        differences_count = 0
        level_data = getLevelData(self.current_level)
        for i in range(y):
            for j in range(x + 1):
                if self.current_level_data.get(key_v)[i][j] != level_data.get(key_v)[i][j]:
                    differences_count += 1
        for i in range(y + 1):
            for j in range(x):
                if self.current_level_data.get(key_h)[i][j] != level_data.get(key_h)[i][j]:
                    differences_count += 1
        if self.current_level_data.get('type') == 'move':
            differences_count = differences_count // 2
        return differences_count

    def checkSquare(self, size, i, j):
        is_square = True
        horizontal_sticks = self.current_level_data.get(key_h)
        vertical_sticks = self.current_level_data.get(key_v)
        for s in range(size):  # проверка каждой спички в зависимости от размера
            if not (horizontal_sticks[i][j] == 1 and horizontal_sticks[i][j + s] == 1 and
                    horizontal_sticks[i + size][j] == 1 and horizontal_sticks[i + size][j + s] == 1 and
                    vertical_sticks[i][j] == 1 and vertical_sticks[i + s][j] == 1 and
                    vertical_sticks[i][j + size] == 1 and vertical_sticks[i + s][j + size] == 1):
                is_square = False
        return is_square

    def squares(self):
        count = 0
        # равные квадраты по заданию
        if self.current_level_data.get('equal'):
            for size in range(1, min(x, y) + 1):
                count = 0
                for i in range(y):
                    for j in range(x):
                        if i <= y - size and j <= x - size:  # проверка ограничений
                            if self.checkSquare(size, i, j):
                                count += 1
                if count == self.current_level_data.get('squares'):
                    return count
        # любой размер квадратов
        else:
            for size in range(1, min(x, y) + 1):
                for i in range(y):
                    for j in range(x):
                        if i <= y - size and j <= x - size:  # проверка ограничений
                            if self.checkSquare(size, i, j):
                                count += 1
        return count

    def moving(self, select):
        if self.current_level_data.get('type') == 'remove':  # если задача на удаление спичек
            self.current_level_data[select[0]][select[1]][select[2]] = 0
        elif self.current_level_data.get('type') == 'move':  # если задача на перемещение
            # запретить выделять пустые поля
            if (self.current_level_data.get(select[0])[select[1]][select[2]] == 0) and self.last_select == []:
                return
            # первое нажатие
            if self.last_select == []:
                self.last_select = select
                self.drawField()
                return
            # отмена выделения
            if self.last_select == select:
                self.last_select = []
                self.drawField()
                return
            # перемещение спички
            if self.last_select != select and self.last_select != []:
                # если старая позиция = 1 и новая = 0, то поменять местами
                if (self.current_level_data.get(self.last_select[0])[self.last_select[1]][self.last_select[2]] == 1) \
                            and (self.current_level_data.get(select[0])[select[1]][select[2]] == 0):
                    self.current_level_data[self.last_select[0]][self.last_select[1]][self.last_select[2]] = 0
                    self.current_level_data[select[0]][select[1]][select[2]] = 1
                    self.last_select = []
        # проверка прохождения уровня
        if self.differences() == self.current_level_data.get('moves') and self.squares() == self.current_level_data.get('squares'):
            self.alertWin()
        self.drawField()  # обновление поля

    def drawField(self):
        self.label_moves.setText('Ходов сделано: ' + str(self.differences()))  # отображение количества сделанных ходов
        # установка вертикальных спичек
        for i in range(y):
            for j in range(x+1):
                if self.current_level_data.get(key_v)[i][j] == 0:
                    getattr(self, 'vertical_%s' % (str(i)+str(j))).hide()
                    getattr(self, 'button_v%s' % (str(i)+str(j))).setStyleSheet(style_opacity)
                elif self.current_level_data.get(key_v)[i][j] == 1:
                    getattr(self, 'vertical_%s' % (str(i)+str(j))).show()
                    getattr(self, 'button_v%s' % (str(i)+str(j))).setStyleSheet(style_hide)
                getattr(self, 'vertical_%s' % (str(i)+str(j))).setGraphicsEffect(None)
        # установка горизонтальных спичек
        for i in range(y+1):
            for j in range(x):
                if self.current_level_data.get(key_h)[i][j] == 0:
                    getattr(self, 'horizontal_%s' % (str(i) + str(j))).hide()
                    getattr(self, 'button_h%s' % (str(i) + str(j))).setStyleSheet(style_opacity)
                elif self.current_level_data.get(key_h)[i][j] == 1:
                    getattr(self, 'horizontal_%s' % (str(i) + str(j))).show()
                    getattr(self, 'button_h%s' % (str(i) + str(j))).setStyleSheet(style_hide)
                getattr(self, 'horizontal_%s' % (str(i)+str(j))).setGraphicsEffect(None)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(5)
        # отображение тени выделенной спички
        if self.last_select != []:
            if self.last_select[0] == key_h:
                getattr(self, 'horizontal_%s' % str(self.last_select[1]) + str(self.last_select[2])).setGraphicsEffect(shadow)
            elif self.last_select[0] == key_v:
                getattr(self, 'vertical_%s' % str(self.last_select[1]) + str(self.last_select[2])).setGraphicsEffect(shadow)

    def toNextLevel(self):
        if self.current_level < levels_count:
            self.startLevel(self.current_level + 1)
        else:
            self.startLevel(1)

    # уведомление в случаи верного решения
    def alertWin(self):
        messageBox = QMessageBox(self)
        messageBox.setStyleSheet("color: white; font-size: 20px;")
        messageBox.setText('Успех')
        buttonNext = QPushButton('Следующий уровень')
        buttonNext.clicked.connect(self.toNextLevel)
        buttonNext.resize(200, 64)
        messageBox.setStandardButtons(QMessageBox.StandardButton.Ok)
        messageBox.addButton(buttonNext, QMessageBox.ButtonRole.AcceptRole)
        messageBox.show()


def application():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    application()
