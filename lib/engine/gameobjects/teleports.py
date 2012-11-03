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
        

class Teleport(GameObject, Solid, Savable):
    radius = TILESIZE
    BLOCKTILES = Player.BLOCKTILES + ['water']
    min_dist = 10
    def __init__(self, position, dest):
        GameObject.__init__(self, position)
        self.dest = dest
    
    def handle_creating(self):
        self.location.teleports.append(self.position)
    
    @wrappers.player_filter(Guided)
    def collission(self, player):
        self.location.game.change_location(player, self.dest)
    

    @classmethod
    def choice_chunk(cls, location, chunk):
        if len(chunk.gt_list(Teleport))>0:
            return False
        return True


    
    def remove(self):
        GameObject.remove(self)
        return True

    def __save__(self):
        return [self.position.get(), self.dest]
    
    @staticmethod
    def __load__((x,y), dest):
        return [Point(x,y), dest]

class Cave(Teleport):
    pass
    
class Stair(Teleport):
    pass

class UpStair(Teleport):
    pass

class DeepCave(Teleport):
    pass