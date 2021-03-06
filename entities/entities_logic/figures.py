from entities.entities_logic.entity import Entity, AttackEntity
from entities.entities_logic.moving_entity import MovingEntity

import random


class Cannon(Entity):
    def __init__(self):
        super().__init__()
        self.attack_range = 200
        self.attack_strength = 12
        self.attack_cooldown = 4
        self.skin_dir = "assets/tower.png"
        self.set_friendly()


class Gendalf(Entity):
    def __init__(self):
        super().__init__()
        self.attack_range = 200
        self.attack_strength = 100
        self.attack_cooldown = 100
        self.skin_dir = "assets/gendalf.png"
        self.set_friendly()
        self.attacking_entity_type = MagicAttack

    def search_target_uuids(self):
        """
        :return: ищет сущностей по радиусу действия
        """
        targets = set()
        for uuid in self.entities.keys():
            if uuid not in self.friends:
                enemy_cords = self.entities[uuid].coordinates
                if self._coordinates_in_radius(enemy_cords):
                    targets.add(uuid)
        return targets

    def do_attack(self):
        """
        :return: попробовать совершить атаку по радиусу
        """
        if not self.current_cooldown:
            targets_uuids = self.search_target_uuids()
            if targets_uuids:
                for target_uuid in targets_uuids:
                    self.on_entity_attack(target_uuid)
                self.current_cooldown = self.attack_cooldown
        else:
            self.current_cooldown -= 1


class MagicAttack(AttackEntity):
    def __init__(self, parent_id, target_id):
        super().__init__(parent_id, target_id)
        self.skin_dir = "assets/magic.png"
        self.speed = 12
        self.on_end_of_route_event.clear()
        self.on_end_of_route_event.add(self.cast_magic)

    def cast_magic(self, _):
        self.cast_effect(self.target_id, "Slowness", 10, 3)
        self.cast_effect(self.target_id, "Poison", 10, 3)


class Zombie(MovingEntity):
    def __init__(self, road_map):
        super().__init__(road_map)
        self.speed = 3
        self.max_health_points = 200
        self.health_points = self.max_health_points
        self.attack_strength += \
            random.randint(0, 10)
        self.wallet = 3 + random.randint(0, 7)


class Boss(Zombie):
    def __init__(self, road_map):
        super().__init__(road_map)
        self.max_health_points = 2000
        self.health_points = self.max_health_points
        self.wallet = 500
        self.attack_strength = 80
        self.speed = 2


class Golem(MovingEntity):
    def __init__(self, road_map):
        super().__init__(road_map)
        self.skin_dir = "assets/golem.png"
        self.speed = 1
        self.on_end_of_route_event.clear()
        self.attack_range = 10
        self.attack_strength = 40
        self.max_health_points = 100
        self.set_friendly()
        self.on_entity_attack_event.add(self.back_attack)

    def back_attack(self, uuid):
        health_loss = Entity.entities[uuid].attack_strength
        self.get_damage(health_loss // 2, uuid)

    def tick(self):
        if len(self.road_map) - self.priority >= 120:
            self.do_move()
        self.do_attack()


class MonsterHealer(MovingEntity):
    def __init__(self, road_map):
        super().__init__(road_map)
        self.speed = 1
        self.skin_dir = "assets/healer.png"
        self.max_health_points = 400
        self.health_points = self.max_health_points
        self.attack_strength = 1
        self.wallet = 30
        self.attack_range = 35
        self.attack_cooldown = 8

        self.attacking_entity_type = HealAttack

    @property
    def priority(self):
        return self.distance * 2

    def tick(self):
        self.do_move()
        self.do_attack()


class MonsterRusher(Zombie):
    def __init__(self, road_map):
        super().__init__(road_map)
        self.speed = 5
        self.skin_dir = "assets/rusher.png"
        self.attack_range = 40
        self.attack_cooldown = 8
        self.attacking_entity_type = SpeedAttack

    def tick(self):
        self.do_move()
        self.do_attack()


class HealAttack(AttackEntity):
    def __init__(self, parent_id, target_id):
        try:
            super().__init__(parent_id, target_id)
            self.skin_dir = "assets/heal.png"
            self.speed = 4
            self.on_end_of_route_event.clear()
            self.on_end_of_route_event.add(self.cast_magic)
        except AttributeError:
            try:
                Entity.entities.pop(self.uuid)
            except KeyError:
                pass

    def cast_magic(self, _):
        self.cast_effect(self.target_id, "HealInstantly", 1, 3)
        self.cast_effect(self.target_id, "Regeneration", 45, 5)


class SpeedAttack(AttackEntity):
    def __init__(self, parent_id, target_id):
        try:
            super().__init__(parent_id, target_id)
            self.skin_dir = "assets/speed.png"
            self.speed = 5
            self.on_end_of_route_event.clear()
            self.on_end_of_route_event.add(self.cast_magic)
        except AttributeError:
            try:
                Entity.entities.pop(self.uuid)
            except KeyError:
                pass

    def cast_magic(self, _):
        self.cast_effect(self.target_id, "Swiftness", 1, 3)
