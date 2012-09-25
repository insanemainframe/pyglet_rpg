#!/usr/bin/env python
# -*- coding: utf-8 -*-
from engine.engine_lib import *
from movable import Movable

from config import *

class Item(StaticObject, Solid):
    radius = TILESIZE
    def __init__(self, position):
        name = 'item_%s' % Item.counter
        Item.counter+=1
        StaticObject.__init__(self, name, position)
    
    def collission(self, player):
        if isinstance(player, Guided):
            self.effect(player)
            self.REMOVE = True
    
    def effect(self, player):
        pass
    
    def remove(self):
        return True

Item.counter = 0

class Ball(Temporary, Solid, Movable,GameObject, Fragile, Mortal, DiplomacySubject):
    "класс снаряда"
    radius = TILESIZE/2
    speed = 60
    BLOCKTILES = ['stone', 'forest']
    def __init__(self, name, position, direct, fraction, damage = 2):
        GameObject.__init__(self, name, position)
        Movable.__init__(self, self.speed)
        Temporary.__init__(self, 10)
        Mortal.__init__(self, damage)
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
    
    def complete_round(self):
        if self.alive:
            Movable.complete_round(selfws390)
    

    def collission(self, player):
        if self.alive:
            Mortal.collission(self, player)

    
    def remove(self):
        return True

        
                    


class DarkBall(Ball):
    radius = TILESIZE/3
    speed = 30
    

class Corpse(StaticObject, Temporary):
    def __init__(self, name, position):
        StaticObject.__init__(self, name, position)
        Temporary.__init__(self, 60)
    
    def update(self):
        if not self.REMOVE:
            StaticObject.update(self)
        Temporary.update(self)

class HealPotion(Item):
    hp = 5
    def effect(self, player):
        player.heal(self.hp)

class SpeedPotion(Item):
    speed = 5
    def effect(self, player):
        player.plus_speed(self.speed)
    
class Sword(Item):
    damage = 1
    def effect(self, player):
        player.plus_damage(self.damage)

class Gold(Item):
    pass

class Armor(Item):
    armor = 3
    def effect(self, player):
        player.plus_hp(self.armor)

class Sceptre(Item):
    pass
    
