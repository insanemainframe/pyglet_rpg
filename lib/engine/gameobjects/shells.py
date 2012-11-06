#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from engine.enginelib.meta import *
from engine.enginelib.movable import Movable

from weakref import ProxyType

from config import *

class Shell(GameObject, Movable, DiplomacySubject, Temporary, Solid, Mortal, ActiveState):
     counter = 0
     def __init__(self, direct, speed, fraction, striker, damage, alive_after_collission):
        assert isinstance(striker, ProxyType)
        GameObject.__init__(self)
        Temporary.mixin(self, 1)
        Movable.mixin(self, self.speed)
        Mortal.mixin(self, damage, alive_after_collission)
        DiplomacySubject.mixin(self, fraction)
        one_step = Point(self.speed, self.speed)
        self.direct = direct*(abs(one_step)/abs(direct))
        self.alive = True
        self.striker = striker
    
     def collission(self, player):
        if isinstance(player, Breakable):
            player.move(self.direct)
            Mortal.collission(self, player)





class Ball(Fragile,  Shell):
    "снаряд игрока"
    radius = TILESIZE/2
    speed = 60
    BLOCKTILES = ['stone', 'forest']
    explode_time = 20
    alive_after_collission = False
    def __init__(self, direct, fraction, striker, damage = 2):
        Shell.__init__(self,direct, self.speed, fraction, striker, damage, self.alive_after_collission)
        
    
    def update(self):
        Movable.move(self, self.direct)
        Movable.update(self)
        Temporary.update(self)
            
    
    
    def collission(self, player):
        Mortal.collission(self, player)
                
    
    def tile_collission(self, tile):
        self.add_to_remove()

    def handle_remove(self):
        return ('explode', self.explode_time)


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

