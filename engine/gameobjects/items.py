#!/usr/bin/env python
# -*- coding: utf-8 -*-
from engine.engine_lib import *
from movable import Movable

from config import *

class Ball(Temporary, Movable,GameObject, Fragile, Mortal, DiplomacySubject):
    "класс снаряда"
    radius = TILESIZE/2
    speed = 60
    BLOCKTILES = ['stone', 'forest']
    def __init__(self, name, position, direct, fraction):
        GameObject.__init__(self, name, position)
        Movable.__init__(self, self.speed)
        Temporary.__init__(self, 10)
        Mortal.__init__(self, 2)
        DiplomacySubject.__init__(self, fraction)
        one_step = Point(self.speed, self.speed)
        self.direct = direct*(abs(one_step)/abs(direct))
        self.alive = True
        self.explode_time = 7*3
    
    def update(self):
        if self.alive:
            Movable.move(self, self.direct)
            Movable.update(self)
            Temporary.update(self)
        else:
            if self.explode_time>0:
                self.add_event(self.position, NullPoint, 'explode', [])
                self.explode_time-=1
            else:
                self.REMOVE
    
    def collission(self):
        self.alive = False
    
    def remove(self):
        return True

        
                    


class DarkBall(Ball):
    radius = TILESIZE/3
    speed = 30
    

class Corpse(StaticObject, Temporary):
    def __init__(self, name, position):
        StaticObject.__init__(self, name, position)
        Temporary.__init__(self, 600)

class HealPotion(Item):
    pass
