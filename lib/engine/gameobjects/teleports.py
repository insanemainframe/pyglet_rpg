#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from random import randrange
from weakref import ProxyType

from engine.enginelib.meta import *
from engine.gameobjects.player import Player

class GetTeleport:
    "фабрика  телепортов"
    __name__ = 'Teleport factory'
    def __init__(self, ttype, dest):
        self.dest = dest
        self.ttype = ttype
        self.BLOCKTILES = ttype.BLOCKTILES
        self.verify_position = ttype.verify_position
    
    def __call__(self):
        return self.ttype(self.dest)
        

class Teleport(GameObject, Solid, Savable):
    radius = TILESIZE
    BLOCKTILES = Player.BLOCKTILES + ['water']
    min_dist = 10
    def __init__(self, dest):
        GameObject.__init__(self)
        self.dest = dest
    
    def handle_new_location(self):
        self.location.teleports.append(self.chunk.cord)
    
    def collission(self, player):
        assert isinstance(player, ProxyType)
        if isinstance(player, Guided):
            self.location.game.change_location(player, location_name = self.dest)
    


    def verify_chunk(cls, location, chunk,):
        if len(chunk.get_list(Teleport))>0:
            return False
        return True


    

    def __save__(self):
        return [ self.dest]
    
    @classmethod
    def __load__(cls, location, dest):
        return cls(dest)

class Cave(Teleport):
    pass
    
class Stair(Teleport):
    pass

class UpStair(Teleport):
    pass

class DeepCave(Teleport):
    pass