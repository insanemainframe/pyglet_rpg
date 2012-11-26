#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from engine.enginelib.meta import *
from engine.enginelib.movable import Movable

from weakref import ProxyType

from config import *
from server_logger import debug


class Shell(BaseObject, Movable, DiplomacySubject, Temporary, Solid, SmartMortal, ActiveState):
    damage = 1
    __lifetime = 1
    
    def __init__(self, direct, impact,  striker, alive_after_collission = False):
        assert isinstance(striker, ProxyType)
        assert isinstance(direct, Position) and bool(direct)

        BaseObject.__init__(self)

        Movable.mixin(self)
        Solid.mixin(self)
        Temporary.mixin(self, self.__lifetime)
        SmartMortal.mixin(self, self.damage, alive_after_collission)
        DiplomacySubject.mixin(self, striker.get_fraction())

        self.set_speed(impact)

        one_step = Position(impact, impact)
        self.direct = direct*(abs(one_step)/abs(direct))

        self.alive = True
        self.striker = striker


    def collission(self, player):
        if isinstance(player, Movable):
            Movable.move(player, self.direct)
        SmartMortal.collission(self, player)


    def __update__(self, cur_time):
        self.move(self.direct)

        Movable.__update__(self, cur_time)
        Temporary.__update__(self, cur_time)

    def __complete_round__(self):
        BaseObject.__complete_round__(self)
        Movable.__complete_round__(self)


class MetaBall(Fragile,  Shell):
    "снаряд игрока"
    def __init__(self, direct, impact, striker, alive_after_collission = False):
        Shell.__init__(self, direct, impact, striker, alive_after_collission)

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

