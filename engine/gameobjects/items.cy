#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *


from engine.enginelib.meta import *
from engine.enginelib.equipment import Equipment
from engine.enginelib import wrappers


class Item(StaticObject, Solid, Temporary):
    radius = TILESIZE
    lifetime = 300
    def __init__(self, position):
        StaticObject.__init__(self, position)
        Temporary.__init__(self, 10*self.lifetime)
    
    def collission(self, player):
        self.world.remove_object(self)
        player.add_item(self)
        
    
    def update(self):
        Temporary.update(self)
    
    def effect(self):
        pass
    
    def remove(self):
        StaticObject.remove(self)
        return True



class Corpse(StaticObject, Temporary):
    "кости остающиеся после смерти живых игроков"
    def __init__(self, name, position):
        StaticObject.__init__(self, position)
        Temporary.__init__(self, 5)
    
    def update(self):
        StaticObject.update(self)
        Temporary.update(self)

class HealPotion(Item):
    "излечивает"
    hp = 5
    def effect(self):
        self.owner.heal(self.hp)

class SpeedPotion(Item):
    "увеличивает скорость"
    speed = 5
    def effect(self):
        self.owner.plus_speed(self.speed)
    
class Sword(Item):
    "увеличивает урон"
    damage = 1
    def effect(self):
        self.owner.plus_damage(self.damage)

class Gold(Item):
    def effect(self):
        self.owner.plus_gold()

class Armor(Item):
    armor = 3
    def effect(self):
        self.owner.plus_hp(self.armor)

class Sceptre(Item):
    def effect(self):
        self.owner.plus_skill()
    
class Cloak(Item):
    invisible_time = 300
    def effect(self):
        self.owner.set_invisible(self.invisible_time)
    
class Lamp(Item):
     def effect(self):
         from engine.gameobjects.units import Ally
         position = self.world.choice_position(Ally, 5, self.owner.position,True)
         ally = Ally(position)
         ally.bind_master(self.owner)
         self.world.new_object(ally)
        
