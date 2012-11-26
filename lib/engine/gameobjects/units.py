#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from server_logger import debug

from engine.enginelib.meta import *
from engine.mathlib import chance
from engine.enginelib.units_lib import *
from engine.gameobjects.items import *
from engine.gameobjects.shells import *
from engine.enginelib.movable import Movable

from weakref import ProxyType


class Ally(Unit, Stalker, Temporary, Walker, Striker, BaseObject, HierarchySubject):
    lifetime = 60
    player_hp = 60
    strike_speed = 3
    strike_impulse = 60

    speed = 40
    look_size = 10
    BLOCKTILES = ['stone', 'forest', ]
    SLOWTILES = {'water':0.5, 'bush':0.3}
    __leash_size = 4

    def __init__(self):   
        Unit.__init__(self, None, self.player_hp, self.speed, 'good')

        HierarchySubject.mixin(self)
        Stalker.mixin(self, self.look_size)
        Striker.mixin(self, self.strike_speed, self.strike_impulse)
        Temporary.mixin(self, self.lifetime)

        self.set_shell(AllyBall)
        self.set_brave()

    def set_leash(self, size):
        assert isinstance(size, int) and size>0

        self.__leash_size = size

    def update_leash(self, value):
        assert isinstance(value, int)

        new_leash - self.__leash_size+value
        if new_leash>0:
            self.__leash_size = new_leash

    def handle_bind_master(self, master):
        self.set_fraction(master.get_fraction())
        debug('ally fraction', self.get_master().get_fraction(), self.get_fraction())
    

    def __update__(self, cur_time):
        if self.has_master():
            master_cord = self.get_master().cord
            self_cord = self.cord
            dist = abs(master_cord-self_cord)
            if dist < self.__leash_size:
                result = self.hunt()
                if result:
                    self.victim, vector = result
                    delta = random()*TILESIZE
                    vector += Position(delta, -delta)
                    self.strike_ball(vector)
                else:
                    self.move(self.get_walk_vector())
            else:
                self.move(master_cord.to_position() - self.position)
        else:
            self.move(self.get_walk_vector())
        
        Unit.__update__(self, cur_time)
        Temporary.__update__(self, cur_time)
    
    def get_args(self):
        return Breakable.get_args(self)
    
    def handle_remove(self):
        HierarchySubject.handle_remove(self)
        Unit.handle_remove(self)


class Cat(Walker, Solid, Stalker, DiplomacySubject, BaseObject, Movable):
    speed = 20
    rainbow_time = 30
    look_size = 300
    heal_speed = 3
    heal_Value = 50
    
    def __init__(self):
        BaseObject.__init__(self)

        Movable.mixin(self, speed=self.speed)
        Solid.mixin(self)
        DiplomacySubject.mixin(self, 'neutral')
        self.prev_heal_time = time()
    
    def collission(self, player):
        if isinstance(player, Unit):
            if not self.is_enemy(player):
                cur_time = time()
                if cur_time - self.prev_heal_time > self.heal_speed:
                    self.prev_heal_time = cur_time
                    self.rainbow(player)
            
    def rainbow(self, player):
        player.heal(self.heal_Value)
        self.add_event('rainbow', self.rainbow_time)
    
    def __update__(self, cur_time):
        if chance(10):
            result = self.hunt(True)
            if result:
                victim, vector = result
                Movable.move(self, vector)
            else:
                self.move(self.get_walk_vector())
        else:
            if not self.get_vector():
                self.move(self.get_walk_vector())

        Movable.__update__(cur_time)
    