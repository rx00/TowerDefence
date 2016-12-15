from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QWidget, QFrame

from entities.entities_logic.entity import Entity


class EntityBridge:
    entities = {}
    last_attack_uuid = -1

    def __init__(self,
                 entity_object,
                 parent=None,
                 show_health=True,
                 static=False,
                 boss=False
                 ):

        # Инициализация технических параметров сущности
        self.entity_logic_object = entity_object
        self.uuid = entity_object.uuid
        self.parent = parent
        self.entities[self.uuid] = self
        self.show_health = show_health
        self.static = static
        self.is_boss = boss
        self.current_attacks = {}

        # Инициализация основного графического объекта
        self.entity_graphic_object = QtEntity(
            self.entity_logic_object,
            self.parent
        )

        # Инициализация отображателя атаки
        self.entity_logic_object.on_attack_summoning_event.add(
            self.tower_attack_listener
        )

        # Попытка отобразить сущность, если у нее предварительно заданы корды
        if len(self.entity_logic_object.coordinates) == 2:
            self.entity_graphic_object.move(
                *self.entity_logic_object.coordinates
            )

        # Инициализация линии HP
        if show_health:
            self.entity_logic_object_health = QtHealth(
                self.parent, boss=boss
            )
            if len(self.entity_logic_object.coordinates) == 2 \
                    and not boss:
                self.entity_logic_object_health.move(
                    *self.entity_logic_object.coordinates
                )
            self.entity_logic_object_health.show()

        # Отрисовка сущности
        self.entity_graphic_object.show()

    def tick(self):
        """
        :return: шина обновления сущностей
        """
        self.entity_logic_object.tick()
        self.entity_graphic_object.move(
            *self.entity_logic_object.coordinates
        )
        if self.show_health:
            self.entity_logic_object_health.on_health_loose(
                self.entity_logic_object.health_points,
                self.entity_logic_object.max_health_points
            )
            if not self.is_boss:
                self.entity_logic_object_health.move(
                    self.entity_logic_object.coordinates[0],
                    self.entity_logic_object.coordinates[1] + 23
                )
        if self.static:
            self.entity_graphic_object.repaint()

    def tower_attack_listener(self, uuid):
        """
        :param uuid: идентификатор цели атаки
        :return: инициализирует сущность снаряда
        """
        try:
            attack_entity = EntityBridge(
                Entity.entities[uuid],
                self.parent,
                show_health=False
            )
            self.current_attacks[uuid] = attack_entity
            attack_entity.entity_logic_object.on_end_of_route_event.\
                add(self.pop_attack)
        except KeyError:
            pass

    def pop_attack(self, attack_uuid):
        """
        :param attack_uuid: id уничтожаемого снаряда
        :return: стирает снаряд с карты и из памяти
        """
        self.current_attacks.pop(attack_uuid)

    def pop(self):
        """
        :return: убивает логическую и графическую сущности
        """
        self.entities.pop(self.uuid)
        self.entity_graphic_object.deleteLater()
        if self.show_health:
            self.entity_logic_object_health.deleteLater()


class QtBasement(QWidget):
    def __init__(self, cords, run_method, parent=None):
        super().__init__(parent)
        self.move(*cords)
        self.current_pixmap = QPixmap("assets/install_active.png")
        self.method = run_method

    def paintEvent(self, event):  # noqa
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.current_pixmap)

    def mousePressEvent(self, event):  # noqa
        self.method(self)

    def sizeHint(self):  # noqa
        return self.current_pixmap.size()


class QtEntity(QWidget):
    def __init__(self, logic_obj_link: Entity, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.pixmap = QPixmap(logic_obj_link.skin_dir)
        self.on_press = None

    def paintEvent(self, event):  # noqa
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def mousePressEvent(self, event):  # noqa
        if self.on_press:
            self.on_press()

    def sizeHint(self):  # noqa
        return self.pixmap.size()


class QtManagePanel(QWidget):
    def __init__(self, x, y, parent=None):
        self.circle = QFrame(parent)
        self.circle.setGeometry(x - 28, y - 28, 70, 70)
        super().__init__(parent)
        self.setGeometry(x - 28, y - 28, 70, 70)
        self.circle.setStyleSheet('''
                 background-color: rgba(0, 0, 0, 200);
                 border-style: solid;
                 border-width:3px;
                 border-radius:37px;
                 border-color: rgba(127, 127, 127, 200);
                 max-width:74;
                 max-height:74;
                 min-width:74;
                 min-height:74;
                 ''')
        self.show()
        self.circle.show()

    def clear(self):
        self.circle.deleteLater()
        self.deleteLater()


class QtHealth(QWidget):
    def __init__(self, parent=None, boss=False):
        super().__init__(parent)
        if not boss:
            self.background_palette = QFrame(self)
            self.rectangle = QFrame(self)
        else:
            self.background_palette = QFrame(self)
            self.rectangle = QFrame(self)
        self.boss = boss
        if not boss:
            self.rectangle.setGeometry(0, 0, 20, 3)
            self.background_palette.setGeometry(-2, -2, 22, 5)
            self.rectangle.setStyleSheet(
                "QWidget { background-color: %s }" % "Green"
            )
        else:
            self.setGeometry(200, 440, 400, 6)
            self.rectangle.setGeometry(0, 0, 400, 6)
            self.background_palette.setGeometry(0, 0, 400, 6)
            self.rectangle.setStyleSheet(
                "QWidget { background-color: %s }" % "Purple"
            )

        self.background_palette.setStyleSheet(
            "QWidget { background-color: %s }" % "Black"
        )

    def on_health_loose(self, health, max_health):
        if not self.boss:
            graphic_health = int((health / max_health) * 20) + 1
            self.rectangle.resize(graphic_health, 3)
            self.update_health_color(graphic_health)
        else:
            graphic_health = int((health / max_health) * 400) + 1
            self.rectangle.resize(graphic_health, 6)

    def update_health_color(self, health):
        self.rectangle.setStyleSheet(
            "QWidget { background-color: %s }" %
            self.get_health_color(health)
        )

    @staticmethod
    def get_health_color(amt):
        if amt >= 20:
            return "Green"
        if amt >= 14:
            return "GreenYellow"
        if amt >= 9:
            return "Yellow"
        if amt >= 4:
            return "Orange"
        if amt >= 0:
            return "Red"
        return "Black"
