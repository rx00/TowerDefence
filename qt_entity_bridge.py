from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QWidget, QFrame
from entities.attack_entities import AttackEntity


class EntityBridge:
    entities = {}
    last_attack_uuid = -1

    def __init__(self, entity_object, parent=None, show_health=True):

        self.entity_logic_object = entity_object
        self.uuid = entity_object.uuid
        self.parent = parent
        self.entities[self.uuid] = self
        self.entity_graphic_object = QtEntity(
            self.entity_logic_object.skin_dir,
            self.parent
        )
        self.entity_logic_object.run_on_entity_attack.add(self.attack)
        if len(self.entity_logic_object.coordinates) == 2:
            self.entity_graphic_object.move(
                *self.entity_logic_object.coordinates
            )

        self.show_health = show_health
        if show_health:
            self.entity_logic_object_health = QtHealth(
                self.parent
            )
            self.entity_logic_object_health.show()

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
        if self.show_health:
            self.entity_logic_object_health.on_health_loose(
                self.entity_logic_object.health_points
            )
            self.entity_logic_object_health.move(
                self.entity_logic_object.coordinates[0],
                self.entity_logic_object.coordinates[1]+23

            )

    def attack(self, uuid):
        """
        :param uuid: идентификатор цели атаки
        :return: инициализирует сущность снаряда
        """
        attack_entity = EntityBridge(
            AttackEntity(
                EntityBridge.last_attack_uuid,
                self.uuid,
                uuid
            ),
            self.parent,
            show_health=False
        )
        self.current_attacks[self.last_attack_uuid] = attack_entity
        EntityBridge.last_attack_uuid -= 1
        attack_entity.entity_logic_object.run_on_end_of_route.\
            add(self.pop_attack)

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


class QtEntity(QWidget):
    def __init__(self, skin_dir, parent=None):
        super(QtEntity, self).__init__(parent)
        self.pixmap = QPixmap(skin_dir)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()


class QtHealth(QWidget):
    def __init__(self, parent=None):
        super(QtHealth, self).__init__(parent)
        self.rectangle = QFrame(self)
        self.rectangle.setGeometry(0, 0, 20, 3)
        self.rectangle.setStyleSheet(
            "QWidget { background-color: %s }" % "Green"
        )

    def on_health_loose(self, health):
        graphic_health = int(health*0.2)+1
        self.rectangle.resize(graphic_health, 3)
        self.update_health_color(graphic_health)

    def update_health_color(self, health):
        comparator = {
            14: "Orange",
            9: "Yellow",
            4: "Red"
        }
        if health in comparator:
            self.rectangle.setStyleSheet(
                "QWidget { background-color: %s }" % comparator[health]
            )
