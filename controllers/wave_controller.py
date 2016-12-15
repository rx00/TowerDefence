import random

from entities.figures import Zombie, Boss, MonsterHealer, Rusher


class WaveController:
    def __init__(self, waves_json, road_map, controller_link):
        self.app = controller_link.app
        self.controller = controller_link
        self.road_map = road_map
        self.waves_json = waves_json
        self.current_wave = 1
        self.current_commands = []
        self.wait = 0
        self.total_monster_count = None
        self.current_wave_monster_count = None
        self.make_command_list()

    def make_command_list(self):
        if self.total_monster_count is None:
            self.total_monster_count = 0
            for wave_dict in self.waves_json:
                self.total_monster_count += wave_dict["amount"]

        creatures = self.waves_json[self.current_wave - 1]["creatures"]
        amt = int(self.waves_json[self.current_wave - 1]["amount"])
        period = int(self.waves_json[self.current_wave - 1]["period"])
        self.current_wave_monster_count = amt
        command_list = []
        randomisation = random.sample(
            [x % len(creatures) for x in range(amt)], amt)
        for random_pointer in randomisation:
            command_list.append(creatures[random_pointer])
            new_period = period - (period * 0.1) + (
                (period * 0.01) * random.randint(-100, 30)
            )
            command_list.append(int(new_period))
        command_list.append("end")
        self.current_commands = command_list

    def tick(self):
        if self.wait == 0 and self.current_commands:
            command = self.current_commands[0]
            self.current_commands = self.current_commands[1:]
            # типичный зомби, иногда - хилер
            if command == "zombie":
                unique_chance = random.randint(0, 100)
                if unique_chance >= 90:
                    monster = MonsterHealer(self.road_map, self.app)
                elif 70 <= unique_chance <= 80:
                    monster = Rusher(self.road_map, self.app)
                else:
                    monster = Zombie(self.road_map, self.app)
                monster.entity_logic_object.on_end_of_route_event.add(
                    self.controller.decrease_health
                )
                monster.entity_logic_object.on_despawn_event.add(
                    self.controller.dec_monster_counter
                )
            # конец волны
            elif command == "end":
                if self.current_wave != len(self.waves_json):
                    self.current_wave += 1
                    self.make_command_list()
            elif command == "boss":
                boss = Boss(self.road_map, self.app)
                boss.entity_logic_object.on_end_of_route_event.add(
                    self.controller.decrease_health
                )
                boss.entity_logic_object.on_despawn_event.add(
                    self.controller.dec_monster_counter
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
