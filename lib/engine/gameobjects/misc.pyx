#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from random import randrange

from share.mathlib cimport Point
from engine.mathlib import chance

from engine.enginelib.meta import StaticObject, Solid, Impassable
from engine.gameobjects.player import Player
from engine.enginelib import wrappers


class Misc(StaticObject):
    BLOCKTILES = Player.BLOCKTILES
    def __init__(self, position):
        StaticObject.__init__(self, position)
        self.number = randrange(self.count)
    
    @classmethod
    def choice_position(cls, world, location, i ,j):
        if len(world.tiles[Point(i,j)]):
            return False
        else:
            return True

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
        cdef str tile

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

class WindMill(Misc):
    BLOCKTILES = Player.BLOCKTILES + ['water']
    count = 1

class AloneBush(Misc, Solid):
    BLOCKTILES = Player.BLOCKTILES + ['water']
    count = 9
    radius = TILESIZE
    def __init__(self, position):
        Misc.__init__(self, position)
        Solid.__init__(self, self.radius)

class AloneTree(Misc, Impassable):
    BLOCKTILES = Player.BLOCKTILES + ['water']
    count = 5
    radius = TILESIZE
    def __init__(self, Point position):
        Misc.__init__(self, position)
        Impassable.__init__(self, self.radius)

    @classmethod
    def choice_position(cls, world, location, i ,j):
        cdef tuple ij

        if len(world.tiles[Point(i,j)]):
            return False

        for ij in world.get_near_cords(i,j):
                for player in world.tiles[Point(*ij)]:
                    if isinstance(player, AloneTree):
                        return True
        if chance(98):
            return False
        else:
            return True
