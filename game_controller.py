from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QLabel


from road_map import RoadMap
from entities.moving_entity import Entity, MovingEntity
from qt_entity_bridge import EntityBridge

import json
import zipfile
import configparser


class GameController:
    def __init__(self, main_window_link: QWidget, map_file):
        self.uuids = 3
        self.app = main_window_link
        self.map_name = None
        self.map_background = None
        self.road_map = None
        self.health = 100
        self.money = 0

        # Init objects
        self.unzip_map(map_file)
        self.set_window_background()
        self.init_gui_elements()

    def init_gui_elements(self):
        # Init status bar
        self.status_bar_label = QLabel(self.app)
        pixmap = QtGui.QPixmap("assets/status_bar.png")
        self.status_bar_label.setPixmap(pixmap)
        self.status_bar_label.move(10, 10)

        # Init text labels
        self.health_bar = QLabel(self.status_bar_label)
        self.money_bar = QLabel(self.status_bar_label)

        self.health_bar.setGeometry(50, 5, 40, 20)
        self.money_bar.setGeometry(50, 42, 40, 20)

        self.health_bar.setText(str(self.health))
        self.money_bar.setText(str(self.money))
        font_description = "font-family: Comic Sans MS; color: #B6B6B4;"
        self.health_bar.setStyleSheet(font_description)
        self.money_bar.setStyleSheet(font_description)

        # Show labels
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

    def unzip_map(self, map_file):
        config_file = "config.ini"
        globals_section = "globals"
        if zipfile.is_zipfile(map_file + ".zip"):
            try:
                with zipfile.ZipFile("{}.zip".format(map_file))\
                        as zip_folder:
                    if config_file in zip_folder.namelist():
                        configs = configparser.ConfigParser()
                        configs.read_string(
                            zip_folder.read(config_file).decode()
                        )
                        if globals_section in configs.sections():
                            try:
                                self.__unpacker(
                                    configs,
                                    globals_section,
                                    zip_folder
                                )
                            except KeyError as e:
                                raise ValueError("Отсутствуют конфиг-секции {}"
                                                 .format(e))

                        else:
                            raise ValueError("Не найдены {}".format(
                                globals_section
                            ))
                    else:
                        raise ValueError("Отсутствует файл {}"
                                         .format(config_file))
            except OSError as e:
                raise ValueError("Не удалось прочитать файл {}, ({})!"
                                 .format(map_file, e))
        else:
            raise ValueError("{} не является zip файлом".format(map_file))

    def __unpacker(self, config_object, config_globals_name, archive_object):
        main_config = config_object[config_globals_name]
        self.map_background = archive_object.read(main_config["background"])
        self.road_map = tuple([tuple(x) for x in
                               json.loads(main_config["road_map"])
                               ])
        self.money = int(main_config["balance"])
        self.init_logic_map()
        self.init_figures()

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
