import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))


from entities.moving_entity import Entity


class EntityTests(unittest.TestCase):
    new_entity = Entity(1)
    another_entity = Entity(2)

    def test_entity_damage(self):
        """
        :return: проверка нанесения урона
        """
        attacker_entity = self.another_entity
        starting_health = self.new_entity.health_points
        damage_amt = 2
        self.new_entity.get_damage(damage_amt, attacker_entity.uuid)
        self.assertEqual(
            self.new_entity.health_points, starting_health-damage_amt
        )

    def test_entity_heal(self):
        """
        :return: проверка хила
        """
        starting_health = self.new_entity.health_points
        heal = 2
        self.new_entity.heal(heal)
        self.assertEqual(
            self.new_entity.health_points, starting_health+heal
        )

    def test_search_enemies(self):
        """
        :return: проверка общей механики поиска ближайшей цели
        """
        self.new_entity.coordinates = (0, 0)
        self.another_entity.coordinates = (1, 1)

        self.new_entity.set_friendly()
        self.new_entity.attack_range = 2

        self.found_uuid = 0
        self.another_entity.danger_rate = 1

        self.new_entity.run_on_entity_attack.add(self.founder)
        self.new_entity.tick()
        self.assertEqual(self.found_uuid, self.another_entity.uuid)

        self.found_uuid = 0
        self.another_entity.coordinates = (2, 2)
        self.new_entity.tick()
        self.assertEqual(self.found_uuid, 0)

    def test_spawning(self):
        new_entity = Entity(3)
        current_entity_uuid = new_entity.uuid
        new_entity.set_friendly()
        new_entity.get_damage(150, 2)
        self.assertFalse(current_entity_uuid in Entity.entities)

    def test_bad_uuid(self):
        with self.assertRaises(KeyError):
            bad_entity = Entity(1)

    def test_bad_cords(self):
        with self.assertRaises(ValueError):
            self.new_entity.coordinates = [[-1]]

    def test_friendships(self):
        self.another_entity.set_friendly()
        self.assertTrue(self.another_entity.uuid in Entity.friends)
        self.another_entity.set_unfriendly()
        self.assertFalse(self.another_entity.uuid in Entity.friends)

    def test_cast_effect(self):
        self.new_entity.cast_effect(2, "Regeneration", 10, 2)
        self.assertTrue(
            len(self.another_entity.effect_objects) == 1
        )
        [self.another_entity.effect_tick() for _ in range(11)]
        self.assertTrue(
            len(self.another_entity.effect_objects) == 0
        )

    def founder(self, uuid):
        self.found_uuid = uuid

if __name__ == '__main__':
    unittest.main()