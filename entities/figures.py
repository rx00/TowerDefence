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


class MonsterHealer(EntityBridge):
    def __init__(self, road_map, parent=None):
        super().__init__(logic.MonsterHealer(road_map), parent=parent)


class Golem(EntityBridge):
    def __init__(self, road_map, parent=None):
        super().__init__(logic.Golem(road_map), parent=parent, static=True)


class Rusher(EntityBridge):
    def __init__(self, road_map, parent=None):
        super().__init__(logic.MonsterRusher(road_map), parent=parent)
