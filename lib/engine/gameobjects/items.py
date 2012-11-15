#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from weakref import proxy, ProxyType


from engine.enginelib.meta import *


class Item(GameObject, Solid, Temporary):
    BLOCKTILES = ['stone', 'forest', 'ocean', 'lava']
    radius = TILESIZE
    lifetime = 300
    def __init__(self,):
        GameObject.__init__(self)
        Temporary.mixin(self, 10*self.lifetime)
    
    def collission(self, player):
        if isinstance(player, Container):
            player.bind(self)
            
        
    
    def update(self):
        Temporary.update(self)
    
    def effect(self):
        return True
    




class HealPotion(Item):
    "излечивает"
    __hp = 5
    def effect(self):
        self.owner.heal(self.__hp)
        return True

class SpeedPotion(Item):
    "увеличивает скорость"
    speed = 5
    def effect(self):
        self.owner.update_speed(self.speed)
        return True
    
class Sword(Item):
    "увеличивает урон"
    damage = 1
    def effect(self):
        self.owner.plus_damage(self.damage)
        return True

class Gold(Item):
    def effect(self):
        self.owner.plus_gold()
        return True

class Armor(Item):
    armor = 3
    def effect(self):
        self.owner.plus_hp(self.armor)
        return True

class Sceptre(Item):
    def effect(self):
        self.owner.plus_skill()
        return True
    
class Cloak(Item):
    invisible_time = 300
    def effect(self):
        self.owner.set_invisible(self.invisible_time)
        return True
    
class Lamp(Item):
     def effect(self):
         from engine.gameobjects.units import Ally
         ally = Ally()
         self.owner.bind_slave(proxy(ally))
         self.owner.location.new_object(ally, chunk = self.owner.chunk.cord)
         return True
         



