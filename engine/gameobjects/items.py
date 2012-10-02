#!/usr/bin/env python
# -*- coding: utf-8 -*-
from engine.engine_lib import *
from movable import Movable

from config import *

class Item(StaticObject, Solid, Temporary):
    radius = TILESIZE
    lifetime = 300
    def __init__(self, position):
        if not hasattr(Item, 'item_counter'):
            Item.item_counter = 0

        name = 'item_%s' % Item.item_counter
        Item.item_counter+=1
        StaticObject.__init__(self, name, position)
        Temporary.__init__(self, 10*self.lifetime)
    
    @wrappers.player_filter(Guided)
    def collission(self, player):
        self.effect(player)
        self.REMOVE = True
    
    def update(self):
        Temporary.update(self)
    
    def effect(self, player):
        pass
    
    def remove(self):
        StaticObject.remove(self)
        return True

class Explodable:
    "взрывающийся объект"
    def __init__(self, explode_time):
        self.explode_time = explode_time
        
    def update(self):
        self.add_event('explode', [], self.explode_time)
        self.explode_time-=1
        self.REMOVE = True
        
    def remove(self):
        return True

class Ball(Temporary, Explodable, Solid, Movable,GameObject, Fragile, Mortal, DiplomacySubject):
    "снаряд игрока"
    radius = TILESIZE/2
    speed = 60
    BLOCKTILES = ['stone', 'forest']
    explode_time = 20
    alive_after_collission = False
    def __init__(self, name, position, direct, fraction, striker, damage = 2):
        GameObject.__init__(self, name, position)
        Movable.__init__(self, self.speed)
        Temporary.__init__(self, 10)
        Explodable.__init__(self, self.explode_time)
        Mortal.__init__(self, damage, self.alive_after_collission)
        DiplomacySubject.__init__(self, fraction)
        one_step = Point(self.speed, self.speed)
        self.direct = direct*(abs(one_step)/abs(direct))
        self.alive = True
        self.striker = striker
    
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
                
    
    
    def tile_collission(self, tile):
        self.alive = False


        
                    


class DarkBall(Ball):
    "снаряд лича"
    radius = TILESIZE/3
    speed = 30
    
class SkillBall(Ball):
    radius = TILESIZE
    speed = 70
    alive_after_collission = True


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
    def effect(self, player):
        player.plus_gold()

class Armor(Item):
    armor = 3
    def effect(self, player):
        player.plus_hp(self.armor)

class Sceptre(Item):
    def effect(self, player):
        player.plus_skill()
    
