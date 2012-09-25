#!/usr/bin/env python
# -*- coding: utf-8 -*-
from engine.engine_lib import *
from movable import Movable

from config import *

item_counter = 0
class Item(StaticObject, Solid):
    radius = TILESIZE
    def __init__(self, position):
        name = 'item_%s' % item_counter
        item_counter+=1
        StaticObject.__init__(self, name, position)
    
    @wrappers.player_filter(Guided)
    def collission(self, player):
        self.effect(player)
        self.REMOVE = True
    
    def effect(self, player):
        pass
    
    def remove(self):
        return True

class Explodable:
    "взрывающийся объект"
    def __init__(self, explode_time):
        self.explode_time = explode_time
    def update(self):
        if self.explode_time>0:
                self.add_event(self.position, NullPoint, 'explode', [])
                self.explode_time-=1
            else:
                self.REMOVE
    def remove(self):
        return True

class Ball(Temporary, Explodable, Solid, Movable,GameObject, Fragile, Mortal, DiplomacySubject):
    "снаряд игрока"
    radius = TILESIZE/2
    speed = 60
    BLOCKTILES = ['stone', 'forest']
    explode_time = 7*3
    def __init__(self, name, position, direct, fraction, damage = 2):
        GameObject.__init__(self, name, position)
        Movable.__init__(self, self.speed)
        Temporary.__init__(self, 10)
        Explodable.__init__(self, self.explode_time)
        Mortal.__init__(self, damage)
        DiplomacySubject.__init__(self, fraction)
        one_step = Point(self.speed, self.speed)
        self.direct = direct*(abs(one_step)/abs(direct))
        self.alive = True
    
    @wrappers.alive_only(Explodable)
    def update(self):
        Movable.move(self, self.direct)
        Movable.update(self)
        Temporary.update(self)
            
    
    @wrappers.alive_only()
    def complete_round(self):
        Movable.complete_round(self)
    
    
    @wrappers.alive_only()
    def collission(self, player):
            Mortal.collission(self, player)


        
                    


class DarkBall(Ball):
    "снаряд лича"
    radius = TILESIZE/3
    speed = 30
    

class Corpse(StaticObject, Temporary):
    "кости остающиеся после смерти живых игроков"
    def __init__(self, name, position):
        StaticObject.__init__(self, name, position)
        Temporary.__init__(self, 60)
    
    def update(self):
        StaticObject.update(self)
        Temporary.update(self)

class HealPotion(Item):
    "излечивает"
    hp = 5
    def effect(self, player):
        player.heal(self.hp)

class SpeedPotion(Item):
    "увеличивает скорость"
    speed = 5
    def effect(self, player):
        player.plus_speed(self.speed)
    
class Sword(Item):
    "увеличивает урон"
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
    
