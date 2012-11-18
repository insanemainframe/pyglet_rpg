#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from engine.enginelib.meta import *
from engine.enginelib.mutable import MutableObject

from weakref import ProxyType

from config import *
from server_logger import debug

class Shell(MutableObject, DiplomacySubject, Temporary, Solid, SmartMortal, ActiveState):
    damage = 1
    def __init__(self, direct, impact,  striker, alive_after_collission = False):
        assert isinstance(striker, ProxyType)
        assert isinstance(direct, Position) and bool(direct)

        MutableObject.__init__(self)

        Solid.mixin(self)
        Temporary.mixin(self, 1)
        SmartMortal.mixin(self, self.damage, alive_after_collission)
        DiplomacySubject.mixin(self, striker.get_fraction())


        self.set_speed(impact)

        one_step = Position(impact, impact)
        self.direct = direct*(abs(one_step)/abs(direct))


        self.alive = True
        self.striker = striker

    def collission(self, player):
        if isinstance(player, MutableObject):
            player.move(self.direct)
        SmartMortal.collission(self, player)

    def update(self):
        self.move(self.direct)





class MetaBall(Fragile,  Shell):
    "снаряд игрока"
    def __init__(self, direct, impact, striker, alive_after_collission = False):
        Shell.__init__(self, direct, impact, striker, alive_after_collission)
        
    
    def update(self):
        Shell.update(self)
        Temporary.update(self)
            
    

                
    

    def handle_remove(self):
        return ('explode', 20)

class Ball(MetaBall):
    damage = 2

class AllyBall(MetaBall):
    damage = 1
                    

class DarkBall(MetaBall):
    damage = 1
    
class SkillBall(MetaBall):
    damage = 2
    def __init__(self, direct, impact, striker):
        Shell.__init__(self, direct, impact, striker, True)

