import random
import math

from simulation.direction import Direction



# TODO: extract to settings
TARGET_NUM_SCORE_LOCATIONS_PER_AVATAR = 0.5
SCORE_DESPAWN_CHANCE = 0.02

TARGET_NUM_PICKUPS_PER_AVATAR = 0.5
PICKUP_SPAWN_CHANCE = 0.02


class HealthPickup(object):
    def __init__(self, health_restored=3):
        self.health_restored = health_restored

    def __repr__(self):
        return 'HealthPickup(health_restored={})'.format(self.health_restored)


class Cell(object):
    def __init__(self, location, habitable=True, generates_score=False):
        self.location = location
        self.habitable = habitable
        self.generates_score = generates_score
        self.avatar = None
        self.pickup = None

    def __repr__(self):
        return 'Cell({} h={} s={} a={} p={})'.format(self.location, self.habitable, self.generates_score, self.avatar, self.pickup)

    def __eq__(self, other):
        return self.location == other.location


class WorldMap(object):
    def __init__(self, grid):
        self.grid = grid

    def generate_all_cells(self):
        return (cell for sublist in self.grid for cell in sublist)

    @property
    def all_cells(self):
        return list(self.generate_all_cells())

    def generate_score_cells(self):
        return (c for c in self.generate_all_cells() if c.generates_score)

    def generate_potential_spawn_locations(self):
        return (c for c in self.generate_all_cells() if c.habitable and not c.generates_score and not c.avatar and not c.pickup)

    def generate_pickup_cells(self):
        return (c for c in self.generate_all_cells() if c.pickup)

    def is_on_map(self, location):
        num_cols = len(self.grid)
        num_rows = len(self.grid[0])
        return (0 <= location.y < num_rows) and (0 <= location.x < num_cols)

    def get_cell(self, location):
        if not self.is_on_map(location):
            return None
        cell = self.grid[location.x][location.y]
        assert cell.location == location, 'location lookup mismatch: arg={}, found={}'.format(location, cell.location)
        return cell

    def update(self, num_avatars):
        self.update_score_locations(num_avatars)
        self.update_pickups(num_avatars)

    def update_score_locations(self, num_avatars):
        for cell in self.generate_score_cells():
            if random.random() < SCORE_DESPAWN_CHANCE:
                cell.generates_score = False

        new_num_score_locations = len(list(self.generate_score_cells()))
        target_num_score_locations = int(math.ceil(num_avatars * TARGET_NUM_SCORE_LOCATIONS_PER_AVATAR))
        num_score_locations_to_add = target_num_score_locations - new_num_score_locations
        if num_score_locations_to_add > 0:
            for cell in random.sample(list(self.generate_potential_spawn_locations()), num_score_locations_to_add):
                cell.generates_score = True

    def update_pickups(self, num_avatars):
        target_num_pickups = int(math.ceil(num_avatars * TARGET_NUM_PICKUPS_PER_AVATAR))
        max_num_pickups_to_add = target_num_pickups - len(list(self.generate_pickup_cells()))
        if max_num_pickups_to_add > 0:
            for cell in random.sample(list(self.generate_potential_spawn_locations()), max_num_pickups_to_add):
                if random.random() < PICKUP_SPAWN_CHANCE:
                    cell.pickup = HealthPickup()

    def get_random_spawn_location(self):
        return random.choice(list(self.generate_potential_spawn_locations())).location

    # TODO: cope with negative coords (here and possibly in other places)
    def can_move_to(self, target_location):
        if not self.is_on_map(target_location):
            return False

        cell = self.get_cell(target_location)
        return cell.habitable and not cell.avatar

    def __repr__(self):
        return repr(self.grid)
