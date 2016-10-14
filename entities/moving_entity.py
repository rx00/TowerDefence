from entities.entity import Entity


class MovingEntity(Entity):
    def __init__(self, uuid, road_map: tuple):
        super().__init__(uuid)
        self.speed = 1
        self.road_map = road_map  # ((x, y), (x, y),... (x, y))
        self.distance = 0
        self.skin_dir = "assets/zombie.png"
        self.coordinates = road_map[self.distance]
        self.move_cooldown = 0
        self.run_on_end_event = set()

    @property
    def priority(self):
        return self.distance

    def do_move(self):
        if not self.move_cooldown:
            self.distance += self.speed
            self.coordinates = self.road_map[self.distance]
            if self.distance >= len(self.road_map) - self.speed - 1:
                self.on_end_of_route(self.uuid)
                self.despawn_entity()
        else:
            self.move_cooldown -= 1

    def on_end_of_route(self, despawn_uuid):
        for func in self.run_on_end_event:
            func(despawn_uuid)

    def tick(self):
        self.do_move()
        # self.do_attack()
