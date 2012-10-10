#!/usr/bin/env python
# -*- coding: utf-8 -*-
from engine.engine_lib import *

from config import *

class Item(StaticObject, Solid, Temporary):
    radius = TILESIZE
    lifetime = 300
    def __init__(self, world, position):
        StaticObject.__init__(self, world, position)
        Temporary.__init__(self, 10*self.lifetime)
    
    @wrappers.player_filter(Guided)
    def collission(self, player):
        self.effect(player)
        self.to_remove()
    
    def update(self):
        Temporary.update(self)
    
    def effect(self, player):
        pass
    
    def remove(self):
        StaticObject.remove(self)
        return True



class Corpse(StaticObject, Temporary):
    "кости остающиеся после смерти живых игроков"
    def __init__(self, name, world, position):
        StaticObject.__init__(self, world, position)
        Temporary.__init__(self, 5)
    
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
    
class Cloak(Item):
    invisible_time = 300
    def effect(self, player):
        player.set_invisible(self.invisible_time)


class Teleport(StaticObject, Solid):
    radius = TILESIZE
    BLOCKTILES = ['stone', 'forest', 'ocean']
    def __init__(self, world, position):
        StaticObject.__init__(self, world, position)
    
    @wrappers.player_filter(Guided)
    def collission(self, player):
        print 'teleport', player, self.to_world
        game.change_world(player, self.to_world)
    

        
    def remove(self):
        StaticObject.remove(self)
        return True
class Cave(Teleport):
    to_world = 'underground'
    
class Stair(Teleport):
    to_world = 'ground'
