#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from engine.engine_lib import *
from movable import Movable

from config import *


class Explodable:
    "взрывающийся объект"
    def __init__(self, explode_time):
        self.explode_time = explode_time
        
    def update(self):
        self.add_event(self.position, NullPoint, 'explode', [], self.explode_time)
        self.REMOVE = True
        
    def remove(self):
        return True

class Ball(Temporary, Explodable, Solid, Movable,GameObject, Fragile, Mortal, DiplomacySubject):
    "снаряд игрока"
    radius = TILESIZE/2
    speed = 60
    BLOCKTILES = ['stone', 'forest']
    explode_time = 20
    alive_after_collission = False
    def __init__(self, name, position, direct, fraction, striker, damage = 2):
        GameObject.__init__(self, name, position)
        Movable.__init__(self, self.speed)
        Temporary.__init__(self, 10)
        Explodable.__init__(self, self.explode_time)
        Mortal.__init__(self, damage, self.alive_after_collission)
        DiplomacySubject.__init__(self, fraction)
        one_step = Point(self.speed, self.speed)
        self.direct = direct*(abs(one_step)/abs(direct))
        self.alive = True
        self.striker = striker
    
    @wrappers.alive_only(Explodable)
    def update(self):
        Movable.move(self, self.direct)
        Movable.update(self)
        Temporary.update(self)
            
    
    
    
    @wrappers.alive_only()
    def collission(self, player):
        Mortal.collission(self, player)
                
    
    
    def tile_collission(self, tile):
        self.alive = False


        
                    


class DarkBall(Ball):
    "снаряд лича"
    radius = TILESIZE/3
    speed = 30
    
class SkillBall(Ball):
    radius = TILESIZE
    speed = 70
    alive_after_collission = True

