#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from random import randrange

from engine.mathlib import Cord, Position, ChunkCord, chance

from engine.enginelib.meta import *
from engine.gameobjects.player import Player


class Misc(GameObject, Savable):
    BLOCKTILES = Player.BLOCKTILES
    def __init__(self):
        GameObject.__init__(self)
        self.number = randrange(self.count)
    

    def get_args(self):
        return {'number': self.number}

class Mushroom(Misc):
    BLOCKTILES = Player.BLOCKTILES + ['water']
    count = 12

class Plant(Misc):
    BLOCKTILES = Player.BLOCKTILES + ['water']
    count = 10

class Flower(Misc):
    BLOCKTILES = Player.BLOCKTILES + ['water']
    count = 15

class WaterFlower(Misc):
    count = 9
    BLOCKTILES = ['grass', 'forest', 'bush', 'stone', 'underground', 'lava']

class BigWaterFlower(WaterFlower):
    count = 9
    def verify_position(self, location, chunk, voxel, i ,j):
        for tile in location.get_near_tiles(i,j):
                if tile in self.BLOCKTILES:
                    return False
        return True

class Reef(Misc):
    BLOCKTILES = ['grass', 'forest', 'bush', 'stone', 'underground', 'lava']
    count = 3
    pass

    
class Rubble(Misc):
    count = 3
    BLOCKTILES = Player.BLOCKTILES
    

class Stone(Misc):
    BLOCKTILES = Player.BLOCKTILES + ['water']
    count = 13

class WindMill(Misc):
    BLOCKTILES = Player.BLOCKTILES + ['water']
    count = 1

class AloneBush(Misc, Solid):
    BLOCKTILES = Player.BLOCKTILES + ['water']
    count = 9
    radius = TILESIZE
    def __init__(self):
        Misc.__init__(self)
        Solid.mixin(self, self.radius)

class AloneTree(Misc, Impassable, ):
    BLOCKTILES = Player.BLOCKTILES + ['water']
    gen_counter = 0
    count = 5
    radius = TILESIZE
    hp = 100
    def __init__(self):
        Misc.__init__(self)
        Impassable.mixin(self, self.radius)

    def verify_position(self, location, chunk, voxel, i,j):
        if AloneTree.gen_counter<50:
            AloneTree.gen_counter+=1
            return True
        else:
            for player in sum(voxel.get_nears(), []):
                if isinstance(player, AloneTree):
                    return True
            if chance(98):
                return False
            else:
                return True

