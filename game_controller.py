from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QLabel


from road_map import RoadMap
from entities.moving_entity import Entity, MovingEntity
from qt_entity_bridge import EntityBridge

import json
import sys
import binascii


class GameController:
    def __init__(self, main_window_link: QWidget, map_file):
        self.uuids = 3
        self.app = main_window_link
        self.map_name = None
        self.starting_balance = None
        self.map_background = None
        self.road_map = None
        self.unpack_map(map_file)
        self.health = 100
        self.money = 0
        self.set_window_background()
        self.init_gui_elements()

    def init_gui_elements(self):
        self.status_bar_label = QLabel(self.app)
        pixmap = QtGui.QPixmap("assets/status_bar.png")
        self.status_bar_label.setPixmap(pixmap)
        self.status_bar_label.move(10, 10)

        self.health_bar = QLabel(self.status_bar_label)
        self.money_bar = QLabel(self.status_bar_label)

        self.health_bar.setGeometry(50, 5, 40, 20)
        self.money_bar.setGeometry(50, 42, 40, 20)

        self.health_bar.setText(str(self.health))
        self.money_bar.setText(str(self.money))
        font_description = "font-family: Comic Sans MS; color: #B6B6B4;"
        self.health_bar.setStyleSheet(font_description)
        self.money_bar.setStyleSheet(font_description)
        self.status_bar_label.show()
        self.health_bar.show()
        self.money_bar.show()

    def decrease_health(self, entity_uuid):
        damage = Entity.entities[entity_uuid].attack_strength
        self.health -= damage
        self.health_bar.setText(str(self.health))

    def add_money(self, entity_uuid):
        money = Entity.entities[entity_uuid].wallet
        self.money += money
        self.money_bar.setText(str(self.money))

    def unpack_map(self, map_file):  # make zipper!

        try:
            with open("{}.twm".format(map_file), "r") as json_map:
                read_map = json.load(json_map)
            self.map_background = binascii.a2b_base64(read_map["background"])
            self.starting_balance = read_map["starting_balance"]
            self.map_name = read_map["map_name"]
            self.road_map = tuple([tuple(x) for x in read_map["map_road_map"]])
            self.init_logic_map()
        except OSError:
            sys.exit("Не удалось загрузить файл карты!")
        except IndexError:
            sys.exit("Файл карты поврежден!")
        except ValueError:
            sys.exit("Файл карты поврежден!")
        self.init_figures()  # TODO wave controller

    def init_logic_map(self):
        road_map = RoadMap(self.road_map)
        self.road_map = road_map.step_map

    def init_figures(self):
        self.obj2 = EntityBridge(Entity(2), self.app, static=True)
        self.obj2.entity_logic_object.on_entity_kill_event.add(self.add_money)
        self.obj2.entity_logic_object.coordinates = (300, 50)
        self.obj2.entity_logic_object.attack_range = 200
        self.obj2.entity_logic_object.attack_strength = 20
        self.obj3 = EntityBridge(Entity(1), self.app, static=True)
        self.obj3.entity_logic_object.on_entity_kill_event.add(self.add_money)
        self.obj3.entity_logic_object.coordinates = (210, 200)
        self.obj3.entity_logic_object.attack_range = 200

        self.obj3.entity_logic_object.attack_strength = 20

    def on_tick(self):
        for entity in list(EntityBridge.entities.keys()):
            EntityBridge.entities[entity].tick()
        self.clear_entities()

        if self.app.add_on_tick:
            self.uuids += 1
            a = EntityBridge(MovingEntity(self.uuids, self.road_map), self.app)
            a.entity_logic_object.speed = 3
            a.entity_logic_object.on_end_of_route_event.\
                add(self.decrease_health)
            self.app.add_on_tick = False

    @staticmethod
    def clear_entities():
        for entity_uuid in list(EntityBridge.entities.keys()):
            if entity_uuid not in Entity.entities:
                EntityBridge.entities[entity_uuid].pop()

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
