import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))


from entities.entity import Entity


class EntityTests(unittest.TestCase):
    new_entity = Entity(1)
    another_entity = Entity(2)

    def test_entity_damage(self):
        attacker_entity = self.another_entity
        starting_health = self.new_entity.health_points
        damage_amt = 2
        self.new_entity.get_damage(damage_amt, attacker_entity.uuid)
        self.assertEqual(
            self.new_entity.health_points, starting_health-damage_amt
        )

    def test_entity_heal(self):
        starting_health = self.new_entity.health_points
        heal = 2
        self.new_entity.heal(heal)
        self.assertEqual(
            self.new_entity.health_points, starting_health+heal
        )

    def test_search_enemies(self):
        self.new_entity.coordinates = (0, 0)
        self.another_entity.coordinates = (1, 1)

        self.new_entity.set_friendly()
        self.new_entity.attack_range = 2

        self.found_uuid = 0
        self.another_entity.danger_rate = 1

        self.new_entity.run_on_entity_attack.add(self.founder)
        self.new_entity.tick()
        self.assertEqual(self.found_uuid, self.another_entity.uuid)

    def founder(self, uuid):
        self.found_uuid = uuid

