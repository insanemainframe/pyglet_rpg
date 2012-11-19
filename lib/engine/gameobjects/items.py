#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from server_logger import debug

from weakref import proxy, ProxyType


from engine.enginelib.meta import *


class Item(Containerable, Solid,  Temporary, GameObject):
    BLOCKTILES = ['stone', 'forest', 'ocean', 'lava']
    radius = TILESIZE
    lifetime = 300
    def __init__(self,):
        GameObject.__init__(self)
        Solid.mixin(self)

        Temporary.mixin(self, self.lifetime)
    
    
    
    def __update__(self, cur_time):
        super(Item, self).__update__(cur_time)
    
    def effect(self):
        return True
    




class HealPotion(Item):
    "излечивает"
    __hp = 5
    def effect(self):
        self.get_owner().heal(self.__hp)
        return True

class SpeedPotion(Item):
    "увеличивает скорость"
    speed = 5
    def effect(self):
        self.get_owner().update_speed(self.speed)
        return True
    
class Sword(Item):
    "увеличивает урон"
    damage = 1
    def effect(self):
        self.get_owner().update_damage(self.damage)
        return True

class Gold(Item):
    def effect(self):
        self.get_owner().plus_gold()
        return True

class Armor(Item):
    armor = 3
    def effect(self):
        self.get_owner().update_hp(self.armor)
        return True

class Sceptre(Item):
    def effect(self):
        self.get_owner().plus_skill()
        return True
    
class Cloak(Item):
    invisible_time = 300
    def effect(self):
        self.get_owner().set_invisible(self.invisible_time)
        return True
    
class Lamp(Item):
     def effect(self):
         from engine.gameobjects.units import Ally
         ally = Ally()
         self.get_owner().bind_slave(proxy(ally))
         self.get_owner().location.new_object(ally, chunk = self.get_owner().chunk.cord)
         return True
         



