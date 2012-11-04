#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from random import randrange

from share.point import Point
from engine.mathlib import chance

from engine.enginelib.meta import *
from engine.gameobjects.player import Player
from engine.enginelib import wrappers


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
    @classmethod
    def verify_position(cls, location, chunk, i ,j):
        if GameObject.verify_position(location, chunk, i ,j):
            return False
        for tile in location.get_near_voxels(i,j):
                if tile in cls.BLOCKTILES:
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
        Solid.__init__(self, self.radius)

class AloneTree(Misc, Impassable):
    BLOCKTILES = Player.BLOCKTILES + ['water']
    count = 5
    radius = TILESIZE
    def __init__(self):
        Misc.__init__(self)
        Impassable.__init__(self, self.radius)

    @classmethod
    def verify_position(cls, location, chunk, i ,j):
        if len(location.get_voxel(i,j)):
            return False

        for i,j in location.get_near_cords(i,j):
                for player in location.get_voxel(i,j):
                    if isinstance(player, AloneTree):
                        return True
        if chance(98):
            return False
        else:
            return True
