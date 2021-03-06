# Kings vs Zombies, main object
from entities.entities_logic.effect import Effect
from road_map import RoadMap


class Entity:

    entities = {}
    friends = set()

    def __init__(self):
        self.uuid = id(self)
        if self.uuid in self.entities:
            raise KeyError("Another entity has this ({}) UUID"
                           .format(self.uuid))
        self.entities[self.uuid] = self
        self.skin_dir = "assets/tower.png"

        self.__coordinates = ()

        self.max_health_points = 100
        self.health_points = self.max_health_points

        self.last_attacker_uuid = None
        self.attack_strength = 4
        self.attack_cooldown = 1
        self.current_cooldown = 0
        self.attack_range = 1

        self.danger_rate = 0
        self.speed = 0
        self.wallet = 10

        self.effect_objects = set()
        self.attacking_entity_type = AttackEntity

        # API
        self.on_despawn_event = set()
        self.on_entity_kill_event = set()
        self.on_entity_attack_event = set()
        self.on_attack_summoning_event = set()
        self.on_hp_loose_event = set()

        self.on_entity_attack_event.add(self.summon_attacking_entity)

    @property
    def priority(self):
        """
        :return: приоритет (помогает башням найти самого вкусного монстра)
        """
        return self.danger_rate

    @property
    def coordinates(self):
        """
        :return: текущее местоположение
        """
        return self.__coordinates

    @coordinates.setter
    def coordinates(self, coordinates: tuple):
        if isinstance(coordinates, tuple) and len(coordinates) == 2 and \
                isinstance(coordinates[1], int) and\
                isinstance(coordinates[0], int):
            self.__coordinates = coordinates
        else:
            raise ValueError("Field requires (x, y) tuple!")

    def set_friendly(self):
        """
        :return: делает сущность дружественной игроку -> всем башням игрока
        """
        self.friends.add(self.uuid)

    def set_unfriendly(self):
        """
        :return: делает сущность враждебной игроку
        """
        self.friends.remove(self.uuid)

    def get_damage(self, dmg_points: int, attacker_uuid):
        """
        :param dmg_points: кол-во урона, которое придется получить сущности
        :param attacker_uuid: идентификатор атакующей сущности
        :return: наносит урон сущности
        """
        self.last_attacker_uuid = attacker_uuid
        self.health_points = max(0, self.health_points - dmg_points)
        for func in self.on_hp_loose_event:
            func(self.health_points)
        if self.health_points <= 0:
            try:
                self.entities[self.last_attacker_uuid]\
                    .on_entity_kill(self.uuid)
            finally:
                self.despawn_entity()

    def __get_effect(self, caller_link, effect_id, durability, strength):
        self.effect_objects.add(
            Effect(self, caller_link, effect_id, durability, strength)
        )

    def cast_effect(self, uuid_target, effect_id, durability, strength):
        """
        :param uuid_target: идентификатор цели наложения эффекта
        :param effect_id: идентификатор эффекта
        :param durability: время действия эффекта
        :param strength: сила эффекта
        :return: кастует эффект на цель
        """
        try:
            self.entities[uuid_target]\
                .__get_effect(self, effect_id, durability, strength)
        except KeyError:
            pass

    def heal(self, health_points: int):
        """
        :param health_points: кол-во выдаваемых очков здоровья
        :return: хилит башню
        """
        self.health_points = \
            min(self.health_points + health_points, self.max_health_points)

    def despawn_entity(self):
        """
        :return: удалить
        """
        self.on_despawn(self.uuid)
        if self.uuid in self.friends:
            self.friends.remove(self.uuid)
        if self.uuid in self.entities:
            self.entities.pop(self.uuid)

    def _coordinates_in_radius(self, cords: tuple):
        dx = abs(cords[0] - self.__coordinates[0])
        dy = abs(cords[1] - self.__coordinates[1])
        if dx > self.attack_range:
            return False
        if dy > self.attack_range:
            return False
        if dx + dy <= self.attack_range:
            return True
        return False

    def search_target_uuid(self):
        """
        :return: ищет наиболее вкусную цель
        """
        best_priority = 0
        best_uuid = None
        for uuid in self.entities.keys():
            if uuid not in self.friends and uuid != self.uuid:
                enemy_cords = self.entities[uuid].coordinates
                if self._coordinates_in_radius(enemy_cords):
                    if self.entities[uuid].priority > best_priority:
                        best_priority = self.entities[uuid].priority
                        best_uuid = uuid
        return best_uuid

    def do_attack(self):
        """
        :return: попробовать совершить атаку
        """
        if not self.current_cooldown:
            best_target_uuid = self.search_target_uuid()
            if best_target_uuid:
                self.on_entity_attack(best_target_uuid)
                self.current_cooldown = self.attack_cooldown
        else:
            self.current_cooldown -= 1

    def summon_attacking_entity(self, target_uuid):
        new_attack = self.attacking_entity_type(
            self.uuid,
            target_uuid
        )
        self.on_attack_summoning(new_attack.uuid)

    def effect_tick(self):
        """
        :return: главная шина для тика эффектов
        """
        for effect in list(self.effect_objects):
            effect.tick()

    def tick(self):
        """
        :return: главная шина для тика сущностей
        """
        self.effect_tick()
        self.do_attack()

    def on_attack_summoning(self, attack_uuid):
        for func in self.on_attack_summoning_event:
            func(attack_uuid)

    def on_despawn(self, own_uuid):
        for func in self.on_despawn_event:
            func(own_uuid)

    def on_entity_kill(self, entity_uuid):
        for func in self.on_entity_kill_event:
            func(entity_uuid)

    def on_entity_attack(self, entity_uuid):
        for func in self.on_entity_attack_event:
            func(entity_uuid)


class AttackEntity(Entity):
    def __init__(self, parent_id, target_id):
        super().__init__()

        self.distance = 0
        try:
            self.coordinates = self.entities[parent_id].coordinates
            self.road_map = None

            self.skin_dir = "assets/bullet.png"
            self.speed = 7

            self.parent_id = parent_id
            self.target_id = target_id

            self.update_road_map()
            self.set_friendly()

            self.on_end_of_route_event = set()
            self.on_end_of_route_event.add(self.__attack)
        except KeyError:
            self.despawn_entity()

    @property
    def priority(self):
        return self.distance

    def __attack(self, _):
        if self.target_id in self.entities and self.parent_id in self.entities:
            self.entities[self.target_id].get_damage(
                self.entities[self.parent_id].attack_strength,
                self.parent_id
            )

    def update_road_map(self):
        if self.target_id in self.entities:
            new_road_map = RoadMap((
                self.coordinates,
                self.entities[self.target_id].coordinates
            ))
            self.road_map = new_road_map.step_map
            self.distance = len(self.road_map)
        else:
            self.road_map = self.road_map[self.speed:]
            self.distance -= self.speed

    def do_move(self):
        if self.distance <= self.speed * 2:
            self.on_end_of_route(self.uuid)
            self.despawn_entity()
        else:
            if self.target_id in self.entities:
                self.coordinates = self.road_map[self.speed]
            else:
                self.coordinates = self.road_map[0]

    def on_end_of_route(self, despawn_uuid):
        for func in self.on_end_of_route_event:
            func(despawn_uuid)

    def tick(self):
        self.update_road_map()
        self.do_move()
