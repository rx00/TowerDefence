from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QLabel

from ImageButton import register_button
from road_map import RoadMap
from entities.moving_entity import Entity, MovingEntity
from qt_entity_bridge import EntityBridge, QtBasement

import json
import zipfile
import configparser


class GameController:
    def __init__(self, main_window_link: QWidget, map_file):
        self.app = main_window_link
        self.map_name = None
        self.map_background = None
        self.road_map = None
        self.health = 100
        self.money = 0

        self.map_objects = set()

        # Пре-инициализация карты и ее параметров
        try:
            self.unzip_map(map_file)
        except ValueError as e:
            raise GameControllerError(
                "Ошибка при инициализации карты: {}".format(e)
            )
        self.init_logic_map()
        self.init_basements()
        self.set_window_background()
        self.init_gui_elements()
        self.init_control_panel()

    def init_gui_elements(self):
        # Инициализация статус-бара
        self.status_bar_label = QLabel(self.app)
        pixmap = QtGui.QPixmap("assets/status_bar.png")
        self.status_bar_label.setPixmap(pixmap)
        self.status_bar_label.move(10, 10)

        # Инициализация текстовых полей
        self.health_bar = QLabel(self.status_bar_label)
        self.money_bar = QLabel(self.status_bar_label)

        self.health_bar.setGeometry(50, 5, 40, 20)
        self.money_bar.setGeometry(50, 42, 40, 20)

        self.health_bar.setText(str(self.health))
        self.money_bar.setText(str(self.money))
        font_description = "font-family: Comic Sans MS; color: #B6B6B4;"
        self.health_bar.setStyleSheet(font_description)
        self.money_bar.setStyleSheet(font_description)

        # Инициализация кнопок
        self.pause_button = register_button(
            (740, 10),
            ["assets/button_stop.png", "assets/button_stop.png"],
            self.app,
            self.set_pause
        )
        self.pause_button.resize(40, 40)

        self.play_button = register_button(
            (740, 10),
            ["assets/button_play.png", "assets/button_play.png"],
            self.app,
            self.set_play
        )
        self.play_button.resize(40, 40)

        self.speed_up_button = register_button(
            (680, 10),
            ["assets/speed_up.png", "assets/speed_up.png"],
            self.app,
            self.increase_speed
        )
        self.speed_up_button.resize(40, 40)

        self.speed_down_button = register_button(
            (680, 10),
            ["assets/speed_down.png", "assets/speed_down.png"],
            self.app,
            self.decrease_speed
        )
        self.speed_down_button.resize(40, 40)

        # Инициализация изначального отображения элементов GUI
        self.status_bar_label.show()
        self.health_bar.show()
        self.money_bar.show()
        self.play_button.hide()
        self.pause_button.show()
        self.speed_up_button.show()

    def increase_speed(self):
        self.app.timer.start(15)
        self.speed_up_button.hide()
        self.speed_down_button.show()

    def decrease_speed(self):
        self.app.timer.start(30)
        self.speed_down_button.hide()
        self.speed_up_button.show()

    def set_pause(self):
        self.app.timer.stop()
        self.pause_button.hide()
        self.play_button.show()

    def set_play(self):
        self.app.timer.start(30)
        self.speed_down_button.hide()
        self.speed_up_button.show()
        self.play_button.hide()
        self.pause_button.show()

    def decrease_health(self, entity_uuid):
        damage = Entity.entities[entity_uuid].attack_strength
        self.health -= damage
        self.health_bar.setText(str(self.health))

    def add_money(self, entity_uuid):
        money = Entity.entities[entity_uuid].wallet
        self.money += money
        self.money_bar.setText(str(self.money))

    def unzip_map(self, map_file):
        """
        :param map_file: имя файла с картой
        :return: инициализирует карту
        """
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

    def __unpacker(self,
                   config_object: configparser.ConfigParser,
                   config_globals_name,
                   archive_object: zipfile.ZipFile
                   ):
        """
        :param config_object: объект для парсинга конфигов
        :param config_globals_name: ссылка на глобальный пункт конфигов
        :param archive_object: объект для распаковки
        :return: выставляет игровых полей (при старте игры)
        """
        main_config = config_object[config_globals_name]
        self.map_background = archive_object.read(main_config["background"])
        self.road_map = tuple([tuple(x) for x in
                               json.loads(main_config["road_map"])
                               ])
        self.money = int(main_config["balance"])

    def init_logic_map(self):
        """
        :return: переводит набор точек карты в большой набор точек (на пути)
        """
        road_map = RoadMap(self.road_map)
        self.road_map = road_map.step_map

    def init_basements(self):  # TODO вынести в инициализацию карты
        self.basement2 = QtBasement((300, 50), self.show_control_panel, self.app)
        self.basement2.show()
        self.basement1 = QtBasement((300, 250), self.show_control_panel, self.app)
        self.basement1.show()
        self.basement3 = QtBasement((210, 200), self.show_control_panel, self.app)
        self.basement3.show()

    def on_tick(self):
        for entity in list(EntityBridge.entities.keys()):
            EntityBridge.entities[entity].tick()
        self.clear_entities()

        if self.app.add_on_tick:
            a = EntityBridge(MovingEntity(self.road_map), self.app)
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

    def init_control_panel(self):
        self.control_panel_position = 800
        self.control_panel_position_delta = -1
        self.control_panel = QLabel(self.app)
        self.control_panel.setGeometry(self.control_panel_position, 0, 250, 500)
        self.control_panel\
            .setStyleSheet("background-color: rgba(0, 0, 0, 200);")
        self.control_panel.show()

        self.close_control_panel = register_button(
            (10,10),
            [
                "assets/close_control.png",
                "assets/close_control.png"
            ],
            self.control_panel,
            self.__hide_control_panel
        )
        self.close_control_panel.show()

    def show_control_panel(self, qt_object_link):

        self.control_panel_position_delta = -2
        self.control_panel_position = 800
        self.set_pause()

        if isinstance(qt_object_link, QtBasement):
            self.last_basement = qt_object_link
            self.cannon_bt = register_button(
                (25, 100),
                [
                    "assets/cannon_img.png",
                    "assets/cannon_img.png"
                ],
                self.control_panel,
                self.set_cannon
            )

            self.gendalf_bt = register_button(
                (25, 170),
                [
                    "assets/gendalf_img.png",
                    "assets/gendalf_img.png"
                ],
                self.control_panel,
                self.__hide_control_panel
            )

            self.golem_bt = register_button(
                (25, 240),
                [
                    "assets/golem_img.png",
                    "assets/golem_img.png"
                ],
                self.control_panel,
                self.__hide_control_panel
            )

            self.cannon_bt.show()
            self.gendalf_bt.show()
            self.golem_bt.show()

        self.animation_timer = QtCore.QTimer()
        self.animation_timer.timeout\
            .connect(self.change_control_panel_position)
        self.animation_timer.start(1)

    def set_cannon(self):
        if self.money - 20 >= 0:
            self.money -= 20
            self.money_bar.setText(str(self.money))
            q_basement_cords = (self.last_basement.x(), self.last_basement.y())
            self.last_basement.deleteLater()
            new_tower = EntityBridge(Entity(), self.app, static=True)
            new_tower.entity_logic_object.coordinates = q_basement_cords
            new_tower.tick()
            new_tower.entity_logic_object.attack_range = 200
            new_tower.entity_logic_object.attack_strength = 20
            new_tower.entity_logic_object.on_entity_kill_event.add(
                self.add_money
            )
            self.map_objects.add(new_tower)

    def __hide_control_panel(self):
        self.control_panel_position_delta = 2
        self.control_panel_position = 600
        self.animation_timer = QtCore.QTimer()
        self.animation_timer.timeout\
            .connect(self.change_control_panel_position)
        self.animation_timer.start(1)

    def change_control_panel_position(self):
        if 600 <= self.control_panel_position <= 800:
            self.play_button.repaint()
            self.speed_up_button.repaint()
            self.speed_down_button.repaint()
            self.pause_button.repaint()
            self.control_panel_position += self.control_panel_position_delta
            self.control_panel.move(self.control_panel_position, 0)
        else:
            self.animation_timer.stop()


class GameControllerError(Exception):
    pass
