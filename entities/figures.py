from entities.entities_logic import figures as logic
from entities.qt_entity_bridge import EntityBridge
from entities.qt_entity_bridge import QtBasement as Basement

import random


class Cannon(EntityBridge):
    def __init__(self, parent=None):
        super().__init__(logic.Cannon(), parent=parent, static=True)


class Gendalf(EntityBridge):
    def __init__(self, parent=None):
        super().__init__(logic.Gendalf(), parent=parent, static=True)


class Zombie(EntityBridge):
    def __init__(self, road_map, parent=None):
        super().__init__(logic.Zombie(road_map), parent=parent)
        self.entity_graphic_object.show()
        self.entity_logic_object.speed = 3
        self.entity_logic_object.health = 200
        self.entity_logic_object.attack_strength += \
            random.randint(0, 10)
        self.entity_logic_object.wallet = 3 + random.randint(0, 7)

