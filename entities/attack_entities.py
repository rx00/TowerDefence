from entities.moving_entity import MovingEntity


class AttackEntity(MovingEntity):
    def __init__(self, uuid, road_map: tuple):
        super().__init__(uuid, road_map)
        self.skin_dir = "assets/bullet.png"
        self.set_friendly()
        self.speed = 7
