#!/usr/bin/env python
# -*- coding: utf-8 -*-
from engine.engine_lib import *
from random import randrange
from player import Player
from config import *
#Teleport(ttype, dest) - > TeleportType(mapname, position)

class GetTeleport:
    "фабрика  телепортов"
    def __init__(self, ttype, dest):
        self.dest = dest
        self.ttype = ttype
        self.BLOCKTILES = ttype.BLOCKTILES
    
    def __call__(self, world, position):
        return self.ttype(world, position, self.dest)
        

class Teleport(StaticObject, Solid):
    radius = TILESIZE
    BLOCKTILES = Player.BLOCKTILES
    def __init__(self, world, position, dest):
        StaticObject.__init__(self, world, position)
        self.world.teleports.append(position)
        self.dest = dest
    
    @wrappers.player_filter(Guided)
    def collission(self, player):
        game.change_world(player, self.dest)
    

        
    def remove(self):
        StaticObject.remove(self)
        return True

class Cave(Teleport):
    pass
    
class Stair(Teleport):
    pass

class UpStair(Teleport):
    pass

class DownCave(Teleport):
    pass


class Misc(StaticObject):
    BLOCKTILES = Player.BLOCKTILES
    def __init__(self, world, position):
        StaticObject.__init__(self, world, position)
        self.number = randrange(self.count)
    
    def get_args(self):
        return {'number': self.number}

class Mushroom(Misc):
    BLOCKTILES = Player.BLOCKTILES + ['water']
    count = 12

class Plant(Misc):
    BLOCKTILES = Player.BLOCKTILES + ['water']
    count = 10

class WaterFlower(Misc):
    count = 19
    BLOCKTILES = ['grass', 'forest', 'bush', 'stone', 'underground', 'lava']

    
class Rubble(Misc):
    count = 3
    BLOCKTILES = Player.BLOCKTILES
    

class Stone(Misc):
    BLOCKTILES = Player.BLOCKTILES + ['water']
    count = 13

class AloneTree(Misc):
    BLOCKTILES = ['forest', 'bush', 'water', 'ocean']
    count = 13
