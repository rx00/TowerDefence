class RoadMap:
    def __init__(self, raw_road_map):
        self.raw_road_map = raw_road_map  # ((x, y),(x, y),...,(x, y))
        self._steps = ()
        self._fill_road_map()

    @property
    def step_map(self):
        return self._steps

    def _fill_road_map(self):
        first_step = self.raw_road_map[0]
        for waypoint in self.raw_road_map[1:]:
            self._steps += self.generate_line(first_step, waypoint)
            first_step = waypoint
        self._steps += (self.raw_road_map[-1],)

    @staticmethod
    def generate_line(p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        delta_x = abs(x2 - x1)
        delta_y = abs(y2 - y1)

        sign_x = 1 if x1 < x2 else -1
        sign_y = 1 if y1 < y2 else -1

        error = delta_x - delta_y

        line = list()

        while (x1 != x2) or (y1 != y2):
            line.append((x1, y1))

            error2 = error * 2
            if error2 > -delta_y:
                error -= delta_y
                x1 += sign_x

            if error2 < delta_x:
                error += delta_x
                y1 += sign_y

        return tuple(line)
