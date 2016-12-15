import random

from entities.figures import Zombie, Boss


class WaveController:
    def __init__(self, waves_json, road_map, controller_link):
        self.app = controller_link.app
        self.controller = controller_link
        self.road_map = road_map
        self.waves_json = waves_json
        self.current_wave = 1
        self.current_commands = []
        self.wait = 0
        self.make_command_list()

    def make_command_list(self):
        creatures = self.waves_json[self.current_wave - 1]["creatures"]
        amt = int(self.waves_json[self.current_wave - 1]["amount"])
        period = int(self.waves_json[self.current_wave - 1]["period"])
        command_list = []
        randomisation = random.sample(
            [x % len(creatures) for x in range(amt)], amt)
        for random_pointer in randomisation:
            command_list.append(creatures[random_pointer])
            new_period = period - (period * 0.1) + (
                (period * 0.01) * random.randint(-100, 30)
            )
            print(new_period)
            command_list.append(int(new_period))
        command_list.append("end")
        self.current_commands = command_list

    def tick(self):
        if self.wait == 0:
            command = self.current_commands[0]
            self.current_commands = self.current_commands[1:]
            # типичный зомби
            if command == "zombie":
                zombie = Zombie(self.road_map, self.app)
                zombie.entity_logic_object.on_end_of_route_event.add(
                    self.controller.decrease_health
                )
            # конец волны
            elif command == "end":
                if self.current_wave != len(self.waves_json):
                    self.current_wave += 1
                    self.make_command_list()
                else:
                    self.controller.is_last_monster = True
            elif command == "boss":
                boss = Boss(self.road_map, self.app)
                boss.entity_logic_object.on_end_of_route_event.add(
                    self.controller.decrease_health
                )
                boss.entity_logic_object.on_end_of_route_event.add(
                    self.controller.decrease_health
                )
                print("Boss spawned")
            # установить ожидание спавна следующего гада
            elif isinstance(command, int):
                self.wait = command
            # неизвестная команда
            else:
                print("Error: {}".format(command))
        elif self.wait < 0:
            self.wait = 5
        else:
            self.wait -= 1
