import unittest

from simulation.location import Location
from simulation import direction
import simulation.map_generator
from simulation.test.dummy_avatar import DummyAvatarRunner
from simulation.test.maps import InfiniteMap, EmptyMap, ScoreOnOddColumnsMap
from simulation.game_state import GameState
from simulation.action import *
from simulation.avatar.avatar_manager import AvatarManager


ORIGIN = Location(x=0, y=0)
EAST_OF_ORIGIN = Location(x=1, y=0)
NORTH_OF_ORIGIN = Location(x=0, y=1)


class TestAction(unittest.TestCase):
    def setUp(self):
        self.avatar = DummyAvatarRunner(ORIGIN, player_id=1)
        self.other_avatar = DummyAvatarRunner(EAST_OF_ORIGIN, player_id=2)
        self.avatar_manager = AvatarManager([self.avatar, self.other_avatar])

    def test_successful_move_action(self):
        game_state = GameState(InfiniteMap(), self.avatar_manager)
        MoveAction(direction.NORTH).apply(game_state, self.avatar)

        self.assertEqual(self.avatar.location, NORTH_OF_ORIGIN)
        self.assertEqual(self.avatar.events, [MovedEvent(ORIGIN, NORTH_OF_ORIGIN)])

    def test_failed_move_action(self):
        game_state = GameState(EmptyMap(), self.avatar_manager)
        MoveAction(direction.NORTH).apply(game_state, self.avatar)

        self.assertEqual(self.avatar.location, ORIGIN)
        self.assertEqual(self.avatar.events, [FailedMoveEvent(ORIGIN, NORTH_OF_ORIGIN)])

    def test_move_action_to_score_square(self):
        game_state = GameState(ScoreOnOddColumnsMap(), self.avatar_manager)
        self.assertEqual(self.avatar.score, 0)

        MoveAction(direction.EAST).apply(game_state, self.avatar)
        self.assertEqual(self.avatar.score, 1)

        MoveAction(direction.EAST).apply(game_state, self.avatar)
        self.assertEqual(self.avatar.score, 1)

        MoveAction(direction.EAST).apply(game_state, self.avatar)
        self.assertEqual(self.avatar.score, 2)

    def test_successful_attack_action(self):
        m = simulation.map_generator.generate_map(2, 2, 0)
        for a in self.avatar_manager.avatars:
            m.get_cell(a.location).avatar = a
        game_state = GameState(m, self.avatar_manager)
        AttackAction(direction.EAST).apply(game_state, self.avatar)

        target_location = EAST_OF_ORIGIN
        damage_dealt = 1

        self.assertEqual(self.avatar.location, ORIGIN)
        self.assertEqual(self.other_avatar.location, EAST_OF_ORIGIN)

        self.assertEqual(self.avatar.events,
                         [PerformedAttackEvent(
                             self.other_avatar,
                             target_location,
                             damage_dealt)])
        self.assertEqual(self.other_avatar.events, [ReceivedAttackEvent(self.avatar, damage_dealt)])

    def test_failed_attack_action(self):
        game_state = GameState(InfiniteMap(), self.avatar_manager)
        AttackAction(direction.NORTH).apply(game_state, self.avatar)

        target_location = NORTH_OF_ORIGIN

        self.assertEqual(self.avatar.location, ORIGIN)
        self.assertEqual(self.other_avatar.location, EAST_OF_ORIGIN)
        self.assertEqual(self.avatar.events, [FailedAttackEvent(target_location)])
        self.assertEqual(self.other_avatar.events, [])
