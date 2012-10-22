#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from random import randrange

from engine.enginelib.meta import *
from engine.gameobjects.player import Player
from engine.enginelib import wrappers


class Misc(StaticObject):
    BLOCKTILES = Player.BLOCKTILES
    def __init__(self, position):
        StaticObject.__init__(self, position)
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
    @classmethod
    def choice_position(cls, world, location, i ,j):
        for tile in world.get_near_tiles(i,j):
                if tile in cls.BLOCKTILES:
                    return False
        return True

    
class Rubble(Misc):
    count = 3
    BLOCKTILES = Player.BLOCKTILES
    

class Stone(Misc):
    BLOCKTILES = Player.BLOCKTILES + ['water']
    count = 13

class AloneTree(Misc, Solid):
    BLOCKTILES = ['forest', 'bush', 'water', 'ocean']
    count = 13
    radius = TILESIZE
    def __init__(self, position):
        Misc.__init__(self, position)
        Solid.__init__(self, self.radius)
