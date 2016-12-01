import configparser
import json
import zipfile

from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QLabel

from ImageButton import register_button
from controllers.wave_controller import WaveController
from entities.entities_logic.figures import Entity
from entities.qt_entity_bridge import EntityBridge
from entities.figures import Basement, Golem
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
        # Пре-инициализация карты и ее параметров
        try:
            self.unzip_map(map_file)
        except ValueError as e:
            raise GameControllerError(
                "Ошибка при инициализации карты: {}".format(e)
            )
        self.init_logic_map()
        self.set_window_background()
        self.init_wave_controller()
        self.init_gui_elements()
        self.app.mousePressEvent = self.mouse_press_event
        self.on_mouse_press_event = set()

    def init_gui_elements(self):
        # Инициализация статус-бара
        self.status_bar_label = QLabel(self.app)
        pixmap = QtGui.QPixmap("assets/status_bar.png")
        self.status_bar_label.setPixmap(pixmap)
        self.status_bar_label.move(10, 10)

        # Инициализация текстовых полей
        self.health_bar = QLabel(self.status_bar_label)
        self.money_bar = QLabel(self.status_bar_label)
        self.wave_bar = QLabel(self.status_bar_label)
        self.boss_bar_background = QLabel(self.app)
        self.boss_bar_health = QLabel(self.app)

        self.boss_bar_background.setGeometry(150, 740, 200, 5)
        self.boss_bar_health.setGeometry(150, 740, 200, 5)

        self.health_bar.setGeometry(50, 5, 40, 20)
        self.money_bar.setGeometry(50, 42, 40, 20)
        self.wave_bar.setGeometry(20, 79, 60, 20)

        self.health_bar.setText(str(self.health))
        self.money_bar.setText(str(self.money))
        wave_number = "Wave: {}".format(self.wave_controller.current_wave)
        self.wave_bar.setText(wave_number)
        font_description = "font-family: Comic Sans MS; color: #B6B6B4;"
        self.health_bar.setStyleSheet(font_description)
        self.money_bar.setStyleSheet(font_description)
        self.wave_bar.setStyleSheet(font_description)

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

        self.golem_call_button = register_button(
            (750, 200),
            ["assets/golem_button.png", "assets/golem_button.png"],
            self.app,
            self.set_golem_mode
        )
        self.golem_call_button.resize(45, 45)
        self.golem_call_button.show()

        # Инициализация изначального отображения элементов GUI
        self.status_bar_label.show()
        self.health_bar.show()
        self.money_bar.show()
        self.wave_bar.show()
        self.play_button.hide()
        self.pause_button.show()
        self.speed_up_button.show()

    def golem_button_image_handler(self):
        if self.money >= 80:
            self.golem_call_button.change_image("assets/golem_button.png")
        else:
            self.golem_call_button.change_image("assets/golem_inactive.png")

    def set_golem_mode(self):
        self.on_mouse_press_event.add(self.set_golem)

    def set_golem(self, cords):
        if self.money >= 80:
            self.money -= 80
            self.money_bar.setText(str(self.money))
            road_map = self.road_map
            closet_cords = (0, 0, 800, 0)
            for i, cord in enumerate(road_map):
                x1, y1 = cord
                x2, y2 = cords
                length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** (1/2)
                if length <= closet_cords[2]:
                    closet_cords = (x1, y1, length, i)

            road_map = road_map[:closet_cords[3]]
            golem = Golem(tuple(reversed(road_map)), self.app)
            golem.entity_logic_object.on_entity_kill_event.add(
                self.add_money
            )
            self.map_objects.add(golem)
        self.on_mouse_press_event.clear()

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
        self.golem_button_image_handler()

        if not self.is_last_monster:
            self.wave_controller.tick()
            if str(self.wave_controller.current_wave) != \
                    self.wave_bar.text().split()[1]:
                self.wave_bar.setText(
                    "Wave: {}".format(self.wave_controller.current_wave)
                )
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

    def increase_speed(self):
        self.app.timer.start(8)
        self.speed_up_button.hide()
        self.speed_down_button.show()

    def decrease_speed(self):
        self.app.timer.start(15)
        self.speed_down_button.hide()
        self.speed_up_button.show()

    def decrease_health(self, entity_uuid):
        try:
            damage = Entity.entities[entity_uuid].attack_strength
            self.health -= damage
            self.health_bar.setText(str(self.health))
        except KeyError:
            pass

    def add_money(self, entity_uuid):
        try:
            money = Entity.entities[entity_uuid].wallet
            self.money += money
            self.money_bar.setText(str(self.money))
        except KeyError:
            pass

    def set_pause(self):
        self.app.timer.stop()
        self.pause_button.hide()
        self.play_button.show()

    def set_play(self):
        self.app.timer.start(15)
        self.speed_down_button.hide()
        self.speed_up_button.show()
        self.play_button.hide()
        self.pause_button.show()

    def mouse_press_event(self, e):
        x, y = e.pos().x(), e.pos().y()
        for func in list(self.on_mouse_press_event):
            func((x, y))


class GameControllerError(Exception):
    pass
