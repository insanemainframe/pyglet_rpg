#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from random import randrange
from weakref import ProxyType

from engine.enginelib.meta import *
from engine.gameobjects.player import Player
from engine.enginelib import wrappers

class GetTeleport:
    "фабрика  телепортов"
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
    
    def handle_new_world(self):
        self.location.teleports.append(self.chunk.cord)
    
    @wrappers.player_filter(Guided)
    def collission(self, player):
        assert isinstance(player, ProxyType)
        self.location.game.change_location(player, location_name = self.dest)
    

    @classmethod
    def verify_chunk(cls, location, chunk):
        if len(chunk.get_list(Teleport))>0:
            return False
        return True


    
    def remove(self):
        GameObject.remove(self)
        return True

    def __save__(self):
        return [ self.dest]
    
    @staticmethod
    def __load__(dest):
        return [dest]

class Cave(Teleport):
    pass
    
class Stair(Teleport):
    pass

class UpStair(Teleport):
    pass

class DeepCave(Teleport):
    pass