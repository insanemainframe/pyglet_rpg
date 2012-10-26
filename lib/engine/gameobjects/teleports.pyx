#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from random import randrange

from engine.enginelib.meta import StaticObject, Solid,Guided
from engine.gameobjects.player import Player
from engine.enginelib import wrappers

from share.mathlib cimport Point

class GetTeleport:
    "фабрика  телепортов"
    def __init__(self, ttype, dest):
        self.dest = dest
        self.ttype = ttype
        self.BLOCKTILES = ttype.BLOCKTILES
        self.choice_position = ttype.choice_position
    
    def __call__(self, position):
        return self.ttype(position, self.dest)
        

class Teleport(StaticObject, Solid):
    radius = TILESIZE
    BLOCKTILES = Player.BLOCKTILES + ['water']
    min_dist = 10
    def __init__(self, Point position, dest):
        StaticObject.__init__(self, position)
        self.dest = dest
    
    def handle_creating(self):
        self.world.teleports.append(self.position)
    
    def collission(self, player):
        if isinstance(player, Guided):
            self.world.game.change_world(player, self.dest)
    
    @classmethod
    def choice_position(cls, world, location, i ,j):
        cdef Point tpoint
        cdef float dist
        cdef int min_dist
        min_dist = cls.min_dist

        for tpoint in world.teleports:
            dist = abs(Point(i,j)*TILESIZE - tpoint)
            if dist<=min_dist*TILESIZE:
                return False
        return True
        
    
    def remove(self):
        StaticObject.remove(self)
        return True

class Cave(Teleport):
    pass
    
class Stair(Teleport):
    pass

class UpStair(Teleport):
    pass

class DeepCave(Teleport):
    pass