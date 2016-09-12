from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QWidget
from entities.attack_entities import AttackEntity

from entities.entity import Entity
from road_map import RoadMap


class EntityBridge:
    entities = {}
    last_attack_uuid = -1

    def __init__(self, entity_object: Entity, parent=None):
        self.entity_logic_object = entity_object
        self.uuid = entity_object.uuid
        self.parent = parent
        self.entities[self.uuid] = self
        self.entity_graphic_object = QtEntity(
            self.entity_logic_object.skin_dir,
            self.parent
        )
        self.entity_logic_object.on_entity_attack = self.attack
        if len(self.entity_logic_object.coordinates) == 2:
            self.entity_graphic_object.move(
                *self.entity_logic_object.coordinates
            )
        self.entity_graphic_object.show()
        self.current_attacks = {}

    def tick(self):
        """
        :return: шина обновления сущностей
        """
        self.entity_logic_object.tick()
        self.entity_graphic_object.move(
            *self.entity_logic_object.coordinates
        )

    def attack(self, uuid):
        """
        :param uuid: идентификатор цели атаки
        :return: инициализирует сущность снаряда
        """
        attack_trace = RoadMap(
            (
                self.entity_logic_object.coordinates,
                Entity.entities[uuid].coordinates
            ))
        attack_map = attack_trace.step_map
        attack_entity = EntityBridge(
            AttackEntity(
                self.last_attack_uuid,
                attack_map[20:]
            ),
            self.parent
        )
        self.current_attacks[self.last_attack_uuid] = attack_entity
        self.last_attack_uuid -= 1
        attack_entity.entity_logic_object.on_end_of_route = \
            self.pop_attack

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


class QtEntity(QWidget):
    def __init__(self, skin_dir, parent=None):
        super(QtEntity, self).__init__(parent)
        self.pixmap = QPixmap(skin_dir)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()
