import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))

from entities.entities_logic.moving_entity import Entity, MovingEntity
from road_map import RoadMap


class EntityTests(unittest.TestCase):
    new_entity = Entity()
    another_entity = Entity()

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

        self.new_entity.on_entity_attack_event.add(self.founder)
        self.new_entity.tick()
        with self.subTest("Test attack init"):
            self.assertEqual(self.found_uuid, self.another_entity.uuid)

        self.found_uuid = 0
        self.another_entity.coordinates = (2, 2)
        self.new_entity.tick()
        with self.subTest("Test attack fail"):
            self.assertEqual(self.found_uuid, 0)

    def test_spawning(self):
        new_entity = Entity()
        current_entity_uuid = new_entity.uuid
        new_entity.set_friendly()
        new_entity.get_damage(150, self.another_entity.uuid)
        self.assertFalse(current_entity_uuid in Entity.entities)

    def test_bad_cords(self):
        with self.subTest("Bad types"):
            with self.assertRaises(ValueError):
                self.new_entity.coordinates = [[-1]]

        with self.subTest("Big length"):
            with self.assertRaises(ValueError):
                self.new_entity.coordinates = (1, 2, 3)

    def test_friendships(self):
        self.another_entity.set_friendly()
        self.assertTrue(self.another_entity.uuid in Entity.friends)
        self.another_entity.set_unfriendly()
        self.assertFalse(self.another_entity.uuid in Entity.friends)

    def test_cast_effect(self):
        self.new_entity.cast_effect(
            self.another_entity.uuid, "Regeneration", 10, 2
        )
        with self.subTest("Test effect casting"):
            self.assertTrue(
                len(self.another_entity.effect_objects) == 1
            )
        [self.another_entity.effect_tick() for _ in range(11)]
        with self.subTest("Test effect duration"):
            self.assertTrue(
                len(self.another_entity.effect_objects) == 0
            )

    def test_road_map_generation(self):
        waypoints = ((1, 1), (1, 5))
        road_map = RoadMap(waypoints)
        with self.subTest("Test straight line"):
            self.assertEqual(
                road_map.step_map,
                ((1, 1), (1, 2), (1, 3), (1, 4), (1, 5))
                             )

        with self.subTest("Test diagonal line"):
            waypoints = ((1, 1), (5, 5))
            road_map = RoadMap(waypoints)
            self.assertEqual(
                road_map.step_map,
                ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5))
            )

    def test_moving_entity(self):
        waypoints = RoadMap(((1, 1), (5, 5)))
        moving_entity = MovingEntity(waypoints.step_map)
        moving_entity_uuid = moving_entity.uuid
        moving_entity.tick()
        with self.subTest("Test moving"):
            self.assertEqual(moving_entity.coordinates, (2, 2))

        moving_entity.move_cooldown = 4
        [moving_entity.tick() for _ in range(1+4)]
        with self.subTest("Test moving cooldown and priority"):
            self.assertEqual(moving_entity.priority, 2)

        moving_entity.tick()
        with self.subTest("Auto moving entity despawn"):
            self.assertFalse(moving_entity_uuid in MovingEntity.entities)

    def founder(self, uuid):
        self.found_uuid = uuid

if __name__ == '__main__':
    unittest.main()
