#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from server_logger import debug

from random import randrange

from engine.mathlib import Cord, Position, ChunkCord, chance

from engine.enginelib.meta import *
from engine.gameobjects.player import Player
from engine.enginelib.passability import *


class Misc(GameObject, Savable):
    def __init__(self):
        GameObject.__init__(self)
        self.number = randrange(self.count)
    
    def __update__(self, cur_time):
        super(Misc, self).__update__(cur_time)

    def get_args(self):
        return {'number': self.number}

class Mushroom(Misc, OverLand):
    count = 12

class Plant(Misc, OverLand):
    count = 10

class Flower(Misc, OverLand):
    count = 15

class WaterFlower(Misc, OverWater):
    count = 9





class BigWaterFlower(WaterFlower, OverWater, BigObject):
    count = 9
    def verify_position(self, location, chunk, cord, generation = True):
        return (GameObject.verify_position(self, location, chunk, cord, generation) and
                BigObject.verify_position(self, location, chunk, cord, generation))
            
        

class Reef(Misc, OverWater):
    count = 3

    
class Rubble(Misc, OverLand):
    count = 3
    

class Stone(Misc, OverLand):
    count = 13

class WindMill(Misc, OverLand):
    count = 1

class AloneBush(Misc, OverLand):
    count = 9
