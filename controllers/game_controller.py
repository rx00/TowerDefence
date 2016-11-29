import configparser
import json
import zipfile

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QLabel

from ImageButton import register_button
from controllers.wave_controller import WaveController
from entities.entities_logic.figures import Entity
from entities.qt_entity_bridge import EntityBridge, QtManagePanel
from entities.figures import Cannon, Basement, Gendalf
from road_map import RoadMap
from controllers.control_panel_gui import ControlPanel


class GameController:
    def __init__(self, main_window_link: QWidget, map_file):
        self.app = main_window_link
        self.map_name = None
        self.map_background = None
        self.road_map = None
        self.health = 100
        self.money = 0

        self.map_objects = set()
        self.basements = set()

        self.is_last_monster = False
        self.wave_controller = None
        self.manage_panel = None
        # Пре-инициализация карты и ее параметров
        try:
            self.unzip_map(map_file)
        except ValueError as e:
            raise GameControllerError(
                "Ошибка при инициализации карты: {}".format(e)
            )
        self.init_logic_map()
        self.set_window_background()
        self.init_gui_elements()
        self.init_wave_controller()

    def init_gui_elements(self):
        # Инициализация статус-бара
        self.status_bar_label = QLabel(self.app)
        pixmap = QtGui.QPixmap("assets/status_bar.png")
        self.status_bar_label.setPixmap(pixmap)
        self.status_bar_label.move(10, 10)

        self.wave_label = QLabel(self.app)
        self.wave_label.setGeometry(350, 25, 100, 25)
        self.wave_label\
            .setStyleSheet("background-color: rgba(255, 255, 200, 0);"
                           "font-family: Comic Sans MS;"
                           "color: rgba(255, 255, 255, 0);")
        self.wave_label.setAlignment(QtCore.Qt.AlignCenter)
        self.wave_label.setText("0")
        self.wave_label.show()

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

    def show_progressbar_text(self, text):
        self.wave_label.setText(text)
        self.intence = 0
        self.new_timer = QtCore.QTimer()
        self.new_timer.timeout.connect(self.__get_intence)
        self.new_timer.start(3)

    def __get_intence(self):
        self.intence += 1
        growth = max(
            min(-(1/5) * (((self.intence - 880) / 25) ** 2) + 250, 140), 0
        )
        if growth > 0:
            self.wave_label.setStyleSheet(
                "background-color: rgba(255, 255, 200, {});"
                "color: rgba(0, 70, 0, {});".format(
                    int(growth), int(growth))
            )
        else:
            self.new_timer.stop()
            self.wave_label.setStyleSheet(
                "background-color: rgba(255, 255, 200, 0);"
                "color: rgba(0, 70, 0, 0);"
            )

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
        basement_cords = tuple(
            tuple(cords) for cords in json.loads(main_config["basements"])
        )
        for basement_cord in basement_cords:
            new_basement = Basement(
                basement_cord, lambda base: ControlPanel(self, base), self.app
            )
            new_basement.show()
            self.basements.add(new_basement)

        self.wave_controller = json.loads(main_config["waves"])

    def init_logic_map(self):
        """
        :return: переводит набор точек карты в большой набор точек (на пути)
        """
        road_map = RoadMap(self.road_map)
        self.road_map = road_map.step_map

    def init_wave_controller(self):
        self.wave_controller = WaveController(
            self.wave_controller,
            self.road_map,
            self
        )

    def on_tick(self):
        for entity in list(EntityBridge.entities.keys()):
            EntityBridge.entities[entity].tick()
        self.clear_entities()

        if not self.is_last_monster:
            self.wave_controller.tick()
        else:
            print("WIN!")

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

    def show_instruments(self, tower_obj: EntityBridge):
        at_x, at_y = tower_obj.entity_logic_object.coordinates
        if self.manage_panel:
            self.manage_panel.clear()
        self.manage_panel = QtManagePanel(at_x, at_y, self.app)
        self.manage_panel.show()
        self.delete_button = register_button(
            (10, 25),
            [
                "assets/delete_tower.png",
                "assets/delete_tower.png"
            ],
            self.manage_panel,
            lambda _, tower=tower_obj: self.delete_tower(tower)
        )

        self.close_instruments = register_button(
            (58, 5),
            [
                "assets/close_tower_menu.png",
                "assets/close_tower_menu.png"
            ],
            self.manage_panel,
            lambda _: self.clear_manage_panel()
        )
        self.close_instruments.show()
        self.delete_button.show()

    def clear_manage_panel(self):
        self.manage_panel.clear()
        self.manage_panel = None

    def delete_tower(self, tower):
        self.clear_manage_panel()
        tower_cords = tower.entity_logic_object.coordinates
        tower.pop()
        basement = Basement(
            tower_cords, lambda base: ControlPanel(self, base), self.app
        )
        basement.show()

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


class GameControllerError(Exception):
    pass
