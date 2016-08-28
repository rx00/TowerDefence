from PyQt5.QtGui import QPainter, QPixmap, QColor
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QPoint
from entity import Entity


class EntityBridge:
    entities = {}

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
        self.attack_line = QtAttack((10, 10), (20, 20), self.parent)
        self.boole = False

    def tick(self):
        self.entity_logic_object.tick()
        self.entity_graphic_object.move(
            *self.entity_logic_object.coordinates
        )

    def attack(self, uuid):
        #self.attack_line = QtAttack(
        #    self.entity_logic_object.coordinates,
        #    Entity.entities[uuid].coordinates,
        #    self.parent
        #)
        if self.boole:
            self.attack_line.show()
        else:
            self.attack_line.hide()
        self.boole = not self.boole

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
