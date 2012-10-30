#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from random import randrange

from engine.enginelib.meta import *
from engine.gameobjects.player import Player
from engine.enginelib import wrappers

class GetTeleport:
    "фабрика  телепортов"
    def __init__(self, ttype, dest):
        self.dest = dest
        self.ttype = ttype
        self.BLOCKTILES = ttype.BLOCKTILES
        self.choice_position = ttype.choice_position
    
    def __call__(self, position):
        return self.ttype(position, self.dest)
        

class Teleport(StaticObject, Solid, Savable):
    radius = TILESIZE
    BLOCKTILES = Player.BLOCKTILES + ['water']
    min_dist = 10
    def __init__(self, position, dest):
        StaticObject.__init__(self, position)
        self.dest = dest
    
    def handle_creating(self):
        self.world.teleports.append(self.position)
    
    @wrappers.player_filter(Guided)
    def collission(self, player):
        self.world.game.change_world(player, self.dest)
    
    @classmethod
    def choice_position(cls, world, location, i ,j):
        for tpoint in world.teleports:
            dist = abs(Point(i,j)*TILESIZE - tpoint)
            if dist<=cls.min_dist*TILESIZE:
                return False
        return True
        
    
    def remove(self):
        StaticObject.remove(self)
        return True

    def __save__(self):
        return [self.position.get(), self.dest]
    
    @staticmethod
    def __load__(x_y, dest):
        x,y = x_y
        return [Point(x,y), dest]
        

class Cave(Teleport):
    pass
    
class Stair(Teleport):
    pass

class UpStair(Teleport):
    pass

class DeepCave(Teleport):
    pass