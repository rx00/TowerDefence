from entities.moving_entity import Entity
from road_map import RoadMap


class AttackEntity(Entity):
    def __init__(self, uuid, parent_id, target_id):
        super().__init__(uuid)

        self.distance = 0
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
