from entities.entity import Entity


class MovingEntity(Entity):
    def __init__(self, uuid, road_map: tuple):
        super().__init__(uuid)
        self.speed = 1
        self.road_map = road_map  # ((x, y), (x, y),... (x, y))
        self.distance = 0
        self.skin_dir = "assets/zombie.png"
        self.coordinates = road_map[self.distance]

    @property
    def priority(self):
        return self.distance

    def do_move(self):
        self.distance += self.speed
        self.coordinates = self.road_map[self.distance]
        if self.distance >= len(self.road_map) - self.speed - 1:
            self.on_end_of_route(self.uuid)
            self.despawn_entity()

    def on_end_of_route(self, despawn_uuid):
        pass

    def tick(self):
        self.do_move()
        # self.do_attack()
