# Kings vs Zombies, main object
from effect import Effect


class Entity:

    entities = {}
    friends = set()

    def __init__(self, uuid):
        self.uuid = uuid
        if uuid in self.entities:
            raise KeyError("Another entity has this UUID")
        self.entities[uuid] = self
        self.skin_dir = "assets/tower.png"

        self.__coordinates = ()
        self.is_dead = False

        self.max_health_points = 100
        self.health_points = 100

        self.last_attacker_uuid = None
        self.attack_strength = 1
        self.attack_cooldown = 0
        self.current_cooldown = 0
        self.attack_range = 1

        self.danger_rate = 0
        self.speed = 0

        self.effect_objects = set()

        # TODO experience + money system, after release
        # self.wallet = 0
        # self.experience_points = 0
        # self.level = 1

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
        self.__coordinates = coordinates

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
        if self.health_points <= 0:
            try:
                self.entities[self.last_attacker_uuid]\
                    .on_entity_kill(self.uuid)
            except KeyError:
                pass
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
        self.entities[uuid_target]\
            .__get_effect(self, effect_id, durability, strength)

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
        if self.uuid in self.friends:
            self.friends.remove(self.uuid)
        self.entities.pop(self.uuid)
        self.on_despawn()

    def _attack(self, uuid, attacker_uuid):
        self.on_entity_attack(uuid)
        entity_object = self.entities[uuid]
        entity_object.get_damage(self.attack_strength, attacker_uuid)

    def _coordinates_in_radius(self, cords: tuple):  # TODO debug
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
            if uuid not in self.friends:
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
                self._attack(best_target_uuid, self.uuid)
                self.current_cooldown = self.attack_cooldown
        else:
            self.current_cooldown -= 1

    def effect_tick(self):
        """
        :return: главная шина для тика эффектов
        """
        for effect in self.effect_objects:
            effect.tick(self)

    def tick(self):
        """
        :return: главная шина для тика сущностей
        """
        self.effect_tick()
        self.do_attack()

    # Little API for overriding
    def on_despawn(self):
        pass

    def on_entity_kill(self, entity_uuid):
        pass

    def on_entity_attack(self, entity_uuid):
        pass