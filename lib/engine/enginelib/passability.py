#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from server_logger import debug
from engine.errors import *

from engine.mathlib import Cord, Position, ChunkCord, chance


class Groupable(object):
    group_chance = 98

    def verify_position(self, location, chunk, cord, generation = True):
        self_type = self.__class__

        if generation:
            if not hasattr(self_type, 'gen_counter'):
                self_type.gen_counter = 0

            if self_type.gen_counter<50:
                self_type.gen_counter+=1
                return True
            else:
                for player in sum(location.get_near_voxels(cord), []):
                    if isinstance(player, self_type):
                        return True
                if chance(self.group_chance):
                    return False
                else:
                    return True
        else:
            return True


class OverLand(object):
    BLOCKTILES = ['water', 'ocean', 'lava', 'stone']


class OverWater(object):
    BLOCKTILES = ['grass', 'forest', 'bush', 'stone', 'underground', 'lava']


class BigObject(object):
    def verify_position(self, location, chunk, cord, generation = True):
        for tile in location.get_near_tiles(cord):
                if tile in self.BLOCKTILES:
                    return False
        return True