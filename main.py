import sys

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget

from ImageButton import register_button
from controllers.game_controller import GameController


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Kings vs Zombies')
        self.set_window_background("assets/KingsVsZombies.png")
        self.setFixedSize(800, 500)
        self.init_start_buttons()
        self.center()
        self.show()

    def init_start_buttons(self):
        self.btn_start_game = register_button(
            (267, 370),
            [
                "assets/start_game.png",
                "assets/start_on.png",
                "assets/start_over.png"
            ],
            self,
            self.start_game
        )

    def start_game(self):
        self.btn_start_game.deleteLater()
        self.controller = GameController(self, "1000")
        self.set_pause = False
        self.init_game_timer(self.controller.on_tick)

    def init_game_timer(self, target_method):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(target_method)
        self.timer.start(15)

    def set_window_background(self, image):
        pal = self.palette()
        pal.setBrush(QtGui.QPalette.Normal, QtGui.QPalette.Window,
                     QtGui.QBrush(QtGui.QPixmap(image)))
        self.setPalette(pal)
        self.autoFillBackground()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

if __name__ == '__main__':

    application = QApplication(sys.argv)
    application.setWindowIcon(QtGui.QIcon("assets/icon.png"))
    start = MainWindow()
    sys.exit(application.exec_())
