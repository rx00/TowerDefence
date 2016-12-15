from entities.entities_logic import figures as logic
from entities.qt_entity_bridge import EntityBridge
from entities.qt_entity_bridge import QtBasement as Basement # noqa


class Cannon(EntityBridge):
    def __init__(self, parent=None):
        super().__init__(logic.Cannon(), parent=parent, static=True)


class Gendalf(EntityBridge):
    def __init__(self, parent=None):
        super().__init__(logic.Gendalf(), parent=parent, static=True)


class Boss(EntityBridge):
    def __init__(self, road_map, parent=None):
        super().__init__(logic.Boss(road_map), parent=parent, boss=True)


class Zombie(EntityBridge):
    def __init__(self, road_map, parent=None):
        super().__init__(logic.Zombie(road_map), parent=parent)
        self.entity_graphic_object.show()


class Golem(EntityBridge):
    def __init__(self, road_map, parent=None):
        super().__init__(logic.Golem(road_map), parent=parent, static=True)
        self.entity_graphic_object.show()
