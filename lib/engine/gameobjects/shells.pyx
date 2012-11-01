#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from engine.enginelib.meta import ActiveState, DiplomacySubject, Temporary, Solid, Mortal, Fragile, Deadly, DynamicObject
from engine.enginelib.movable import Movable
from engine.enginelib import wrappers

from share.point cimport Point



from config import *

class Shell(ActiveState, Movable, DiplomacySubject, Temporary, Solid, Mortal, Updatable, DynamicObject):
     counter = 0
     def __init__(self, Point position, Point direct, int speed, fraction, striker, damage, alive_after_collission):
        name = "%s_%s" % (self.__class__.__name__, Shell.counter)
        Shell.counter+=1
        
        DynamicObject.__init__(self, name,position)
        Movable.__init__(self, self.speed)
        Mortal.__init__(self, damage, alive_after_collission)
        DiplomacySubject.__init__(self, fraction)
        one_step = Point(self.speed, self.speed)
        self.direct = direct*(abs(one_step)/abs(direct))
        self.alive = True
        self.striker = striker
    
     @wrappers.player_filter(Deadly)
     def collission(self, player):
         player.move(self.direct)
         Mortal.collission(self, player)



class Explodable:
    "взрывающийся объект"
    def __init__(self, explode_time):
        self.explode_time = explode_time
        
    def update(self):
        self.add_event('explode', timeout = self.explode_time)
        self.delayed = True
        self.to_remove()
        
    def remove(self):
        return True

class Ball(Explodable, Fragile,  Shell):
    "снаряд игрока"
    radius = TILESIZE/2
    speed = 60
    BLOCKTILES = ['stone', 'forest']
    explode_time = 20
    alive_after_collission = False
    def __init__(self,Point position, Point direct, fraction, striker, damage = 2):
        Shell.__init__(self,position, direct, self.speed, fraction, striker, damage, self.alive_after_collission)
        Temporary.__init__(self, 1)
        Explodable.__init__(self, self.explode_time)
        
    
    @wrappers.alive_only(Explodable)
    def update(self):
        Movable.move(self, self.direct)
        Movable.update(self)
        Temporary.update(self)
            
    
    
    
    @wrappers.alive_only()
    def collission(self, player):
        Mortal.collission(self, player)
                
    
    
    def tile_collission(self, str tile):
        self.alive = False


class AllyBall(Ball):
    pass
                    


class DarkBall(Ball):
    "снаряд лича"
    radius = TILESIZE/3
    speed = 30
    
class SkillBall(Ball):
    radius = TILESIZE
    speed = 70
    alive_after_collission = True

