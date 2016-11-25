from entities.entities_logic.entity import Entity
from entities.entities_logic.moving_entity import MovingEntity


class Cannon(Entity):
    def __init__(self):
        super().__init__()
        self.attack_range = 200
        self.attack_strength = 3
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

        self.on_entity_attack_event.clear()
        self.on_entity_attack_event.add(self.cast_effects)

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

    def cast_effects(self, uuid):
        self.cast_effect(uuid, "Slowness", 10, 3)
        self.cast_effect(uuid, "Poison", 10, 3)


class Zombie(MovingEntity):
    def __init__(self, road_map):
        super().__init__(road_map)
