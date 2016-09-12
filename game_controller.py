from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget

from road_map import RoadMap

import json
import sys
import binascii


class GameController:
    def __init__(self, main_window_link: QWidget, map_file):
        self.app = main_window_link
        self.map_name = None
        self.starting_balance = None
        self.map_background = None
        self.road_map = None
        self.unpack_map(map_file)
        self.set_window_background()

    def unpack_map(self, map_file):
        with open("{}.twm".format(map_file), "r") as json_map:
            read_map = json.load(json_map)
        self.map_background = binascii.a2b_base64(read_map["background"])
        self.starting_balance = read_map["starting_balance"]
        self.map_name = read_map["map_name"]
        self.road_map = tuple([tuple(x) for x in read_map["map_road_map"]])
        self.init_logic_map()
        self.init_game_timer()

    def init_logic_map(self):
        road_map = RoadMap(self.road_map)
        self.app.road_map = road_map.step_map

    def init_game_timer(self):
        self.app.timer = QtCore.QTimer()
        self.app.timer.timeout.connect(self.app.on_tick)
        self.app.timer.start(30)

    def set_window_background(self):
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(self.map_background)
        pal = self.app.palette()
        pal.setBrush(QtGui.QPalette.Normal, QtGui.QPalette.Window,
                     QtGui.QBrush(pixmap))
        self.app.setPalette(pal)
        self.app.autoFillBackground()


def build_map(image_path, map_name, balance, road_map):
    based_image = binascii.b2a_base64(open(image_path, mode="rb").read())
    map_dict = {
        "background": based_image.decode(),
        "starting_balance": balance,
        "map_name": map_name,
        "road_map": road_map
    }
    with open("{}.twm".format(map_name), 'w') as map_file:
        json.dump(map_dict, map_file)

if __name__ == '__main__':
    build_map(sys.argv[1], sys.argv[2], sys.argv[3])