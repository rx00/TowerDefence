from entities.entities_logic.entity import Entity


class MovingEntity(Entity):
    def __init__(self, road_map: tuple):
        super().__init__()
        self.speed = 1
        self.road_map = road_map  # ((x, y), (x, y),... (x, y))
        self.distance = 0
        self.skin_dir = "assets/zombie.png"
        self.coordinates = road_map[self.distance]
        self.move_cooldown = 0
        self.on_end_of_route_event = set()

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
        for func in self.on_end_of_route_event:
            func(despawn_uuid)

    def tick(self):
        self.effect_tick()
        self.do_move()
        # self.do_attack()
