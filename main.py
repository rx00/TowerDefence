from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from PyQt5 import QtGui
from ImageButton import register_button
from road_map import RoadMap
from qt_entity_bridge import EntityBridge
from moving_entity import MovingEntity, Entity
import sys


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
        self.set_window_background("assets/map_01.png")
        self.init_game_timer()
        self.init_game_map()
        self.init_figures()
        self.add_on_tick = False

    def init_game_timer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.on_tick)
        self.timer.start(30)

    def init_game_map(self):
        waypoints = (
            (-50, 150), (0, 150), (60, 190), (140, 120), (330, 130), (480, 70),
            (720, 150), (720, 320), (550, 400), (450, 300), (280, 410)
        )
        road = RoadMap(waypoints)
        self.road_map = road.step_map

    def init_figures(self):
        self.uuids = 3
        self.obj2 = EntityBridge(Entity(2), self)
        self.obj2.entity_logic_object.coordinates = (300, 50)
        self.obj2.entity_logic_object.attack_range = 200
        self.obj2.entity_logic_object.attack_strength = 5
        self.obj2.entity_logic_object.set_friendly()
        self.obj3 = EntityBridge(Entity(1), self)
        self.obj3.entity_logic_object.coordinates = (210, 200)
        self.obj3.entity_logic_object.attack_range = 200

    def on_tick(self):
        for entity in list(EntityBridge.entities.keys()):
            EntityBridge.entities[entity].tick()
        self.clear_entities()

        if self.add_on_tick:
            self.uuids += 1
            a = EntityBridge(MovingEntity(self.uuids, self.road_map), self)
            a.entity_logic_object.speed = 2
            self.add_on_tick = False

    @staticmethod
    def clear_entities():
        for entity_uuid in list(EntityBridge.entities.keys()):
            if entity_uuid not in Entity.entities:
                EntityBridge.entities[entity_uuid].pop()

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
        if e.key() == Qt.Key_Space:
            self.add_on_tick = True


if __name__ == '__main__':

    application = QApplication(sys.argv)
    application.setWindowIcon(QtGui.QIcon("assets/icon.png"))
    start = MainWindow()
    sys.exit(application.exec_())
