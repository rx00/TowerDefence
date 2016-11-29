from entities.entities_logic.entity import Entity, AttackEntity
from entities.entities_logic.moving_entity import MovingEntity


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
