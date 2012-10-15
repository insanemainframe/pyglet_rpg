#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.engine_lib import *
from engine.mathlib import chance
from engine.gameobjects.units_lib import *
from engine.gameobjects.items import *
from engine.gameobjects.shells import *
from engine.gameobjects.movable import Movable




class Cat(Walker, Solid, Stalker, DynamicObject, DiplomacySubject):
    speed = 20
    radius = TILESIZE
    rainbow_time = 30
    alive = True
    look_size = 300
    
    def __init__(self, name, position):
        DynamicObject.__init__(self, name, position)
        Solid.__init__(self, self.radius)
        Movable.__init__(self, self.speed)
        DiplomacySubject.__init__(self, 'good')
        self.heal_counter = 0
    
    @wrappers.player_filter(Guided)
    def collission(self, player):
        if self.heal_counter==0:
            self.rainbow(player)
        self.heal_counter+=1
        if self.heal_counter==10:
            self.heal_counter = 0
    
    def rainbow(self, player):
        player.heal(5)
        self.add_event('rainbow', timeout = self.rainbow_time)
    
    def update(self):
        if chance(10):
            direct = self.hunt(True)
            Movable.move(self,direct)
        else:
            if not self.vector:
                Walker.update(self)
    
    def complete_round(self):
        Movable.complete_round(self)

class MetaMonster(Respawnable, Lootable, Unit, Stalker, Walker, DynamicObject):
    radius = TILESIZE
    look_size = 10
    BLOCKTILES = ['stone', 'forest', 'ocean', 'lava']
    SLOWTILES = {'water':0.5, 'bush':0.3}
    def __init__(self, name, position, speed, hp):
        DynamicObject.__init__(self, name, position)
        Unit.__init__(self, speed, hp, Corpse, 'monsters')
        Stalker.__init__(self, self.look_size)
        Respawnable.__init__(self, 30, 60)
        Lootable.__init__(self, self.loot_cost)
        
        self.stopped = False
        
        self.spawn()
    
    def hit(self, damage):
        self.stop(10)
        Deadly.hit(self, damage)
    
    @wrappers.alive_only(Deadly)
    def update(self):
        if chance(70):
            direct = self.hunt()
            if direct:
                self.move(direct)
            else:
                Walker.update(self)
        else:
            Walker.update(self)
        Movable.update(self)
        Deadly.update(self)
    
    def get_args(self):
        return Deadly.get_args(self)
    
    def complete_round(self):
        Movable.complete_round(self)
        

class Bat(Fighter, MetaMonster):
    hp = 3
    speed = 30
    damage = 1
    attack_speed = 10
    loot_cost = 10
    BLOCKTILES = ['stone', 'forest']
    SLOWTILES = {}
    
    def __init__(self, name, position):
        MetaMonster.__init__(self, name, position, self.speed, self.hp)
        Fighter.__init__(self, self.damage, self.attack_speed)
    
    def complete_round(self):
        MetaMonster.complete_round(self)
        Fighter.complete_round(self)

class Zombie(Fighter, MetaMonster):
    hp = 20
    speed = 15
    damage = 2
    attack_speed = 10
    loot_cost = 30
    
    def __init__(self, name, position):
        MetaMonster.__init__(self, name, position, self.speed, self.hp)
        Fighter.__init__(self, self.damage, self.attack_speed)
    
    def complete_round(self):
        MetaMonster.complete_round(self)
        Fighter.complete_round(self)
    

class Ghast(Fighter, MetaMonster):
    hp = 50
    speed = 10
    damage = 10
    attack_speed = 30
    loot_cost = 90
    
    def __init__(self, name, position):
        MetaMonster.__init__(self, name, position, self.speed, self.hp)
        Fighter.__init__(self, self.damage, self.attack_speed)
    
    def complete_round(self):
        MetaMonster.complete_round(self)
        Fighter.complete_round(self)


class Lych(MetaMonster, Striker):
    hp = 25
    speed = 10
    damage = 5
    loot_cost = 60
    
    def __init__(self, name, position):
        MetaMonster.__init__(self, name, position, self.speed, self.hp)
        Striker.__init__(self, 10, DarkBall, self.damage)
    
    @wrappers.alive_only(Deadly)
    def update(self):
        if chance(50):
            direct = self.hunt(False)
            if direct:
                delta = random()*TILESIZE
                direct += Point(delta, -delta)
                self.strike_ball(direct)
            else:
                Walker.update(self)
        else:
            Walker.update(self)
            
        Movable.update(self)
        Striker.update(self)
        Deadly.update(self)
    
    def complete_round(self):
        Movable.complete_round(self)
        Striker.complete_round(self)
