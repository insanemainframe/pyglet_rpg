#!/usr/bin/env python
# -*- coding: utf-8 -*-
from engine.engine_lib import *
from random import randrange
from player import Player
from config import *


class Teleport(StaticObject, Solid):
    radius = TILESIZE
    BLOCKTILES = ['stone', 'forest', 'ocean']
    def __init__(self, world, position):
        StaticObject.__init__(self, world, position)
        self.world.teleports.append(position)
    
    @wrappers.player_filter(Guided)
    def collission(self, player):
        print 'teleport', player, self.to_world
        game.change_world(player, self.to_world)
    

        
    def remove(self):
        StaticObject.remove(self)
        return True

class Cave(Teleport):
    to_world = 'underground'
    
class Stair(Teleport):
    to_world = 'ground'


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
    count = 10

class WaterFlower(Misc):
    count = 21
    BLOCKTILES = ['grass', 'forest', 'bush', 'stone', 'underground']

    

class Stone(Misc):
    count = 13
