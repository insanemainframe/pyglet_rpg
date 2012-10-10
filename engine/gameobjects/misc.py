#!/usr/bin/env python
# -*- coding: utf-8 -*-
from engine.engine_lib import *
from random import randrange
from player import Player
from config import *

class Misc(StaticObject):
    BLOCKTILES = Player.BLOCKTILES
    def __init__(self, world, position):
        StaticObject.__init__(self, world, position)
        self.number = randrange(self.count)
    
    def get_args(self):
        return {'number': self.number}

class Mushroom(Misc):
    count = 12

class Plant(Misc):
    count = 32

class WaterFlower(Misc):
    count = 21
    def __init__(self, world, position):
        Misc.__init__(self, world, position)
        self.BLOCKTILES = ['grass', 'forest', 'bush', 'stone', 'underground']
    

class Stone(Misc):
    count = 13
