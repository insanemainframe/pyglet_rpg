#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from server_logger import debug

from engine.enginelib.meta import *
from engine.mathlib import chance
from engine.enginelib.units_lib import *
from engine.gameobjects.items import *
from engine.gameobjects.shells import *
from engine.enginelib.mutable import MutableObject

from weakref import ProxyType


        

class Bat(MetaMonster):
    player_hp = 30
    speed = 30
    damage = 1
    attack_speed = 10
    loot_cost = 10
    BLOCKTILES = ['stone', 'forest']
    SLOWTILES = {}
    
    def __init__(self):
        MetaMonster.__init__(self, self.speed, self.player_hp)
    


class Zombie( MetaMonster):
    player_hp = 200
    speed = 15
    damage = 2
    attack_speed = 10
    loot_cost = 30
    
    def __init__(self):
        MetaMonster.__init__(self, self.speed, self.player_hp)
        

    def __update__(self, cur_time):
        super(Zombie, self).__update__(cur_time)
    

    

class Ghast( MetaMonster):
    player_hp = 500
    speed = 10
    damage = 10
    attack_speed = 30
    loot_cost = 90
    
    def __init__(self):
        MetaMonster.__init__(self, self.speed, self.player_hp)
        Fighter.mixin(self, self.damage, self.attack_speed)

    def __update__(self, cur_time):
        super(Ghast, self).__update__(cur_time)



class Lych(MetaMonster, Striker):
    player_hp = 250
    speed = 10
    damage = 5
    loot_cost = 60
    strike_impulse = 40
    strike_speed = 1
    
    def __init__(self):
        MetaMonster.__init__(self, self.speed, self.player_hp)
        Striker.mixin(self, self.strike_speed, self.strike_impulse)
        self.set_shell(DarkBall)
    
    def __update__(self, cur_time):
        if chance(50):
            result = self.hunt(False)
            if result:
                vector = result[1]
                delta = random()*TILESIZE
                vector += Position(delta, -delta)
                self.strike_ball(vector)
            else:
                self.move(self.get_walk_vector())
        else:
            self.move(self.get_walk_vector())
            
        super(Lych, self).__update__(cur_time)
        
