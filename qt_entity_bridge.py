from PyQt5.QtGui import QPainter, QPixmap, QColor
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QPoint
from attack_entities import AttackEntity
from entity import Entity
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
        self.entity_logic_object.tick()
        self.entity_graphic_object.move(
            *self.entity_logic_object.coordinates
        )

    def attack(self, uuid):
        attack_trace = RoadMap(
            (
                self.entity_logic_object.coordinates,
                Entity.entities[uuid].coordinates
            ))
        attack_map = attack_trace.step_map
        attack_entity = EntityBridge(
            AttackEntity(
                self.last_attack_uuid,
                attack_map
            ),
            self.parent
        )
        self.current_attacks[self.last_attack_uuid] = attack_entity
        self.last_attack_uuid -= 1
        attack_entity.entity_logic_object._on_end_of_route = \
            self.pop_attack

    def pop_attack(self, attack_uuid):
        self.current_attacks.pop(attack_uuid)

    def pop(self):
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


class QtAttack(QWidget):
    def __init__(self, point1, point2, parent=None):
        super(QtAttack, self).__init__(parent)
        self.point1 = QPoint(*point1)
        self.point2 = QPoint(*point2)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QColor("red"))
        painter.drawLine(self.point1, self.point2)
