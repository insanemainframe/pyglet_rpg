#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.enginelib.meta import *
from engine.mathlib import chance
from engine.enginelib.units_lib import *
from engine.gameobjects.items import *
from engine.gameobjects.shells import *
from engine.enginelib.movable import Movable
from engine.enginelib import wrappers



class Ally(Unit, Stalker, Temporary, Walker, Striker, DynamicObject):
    lifetime = 60
    hp = 60
    damage = 5
    speed = 40
    radius = TILESIZE
    look_size = 10
    BLOCKTILES = ['stone', 'forest', 'ocean', 'lava']
    SLOWTILES = {'water':0.5, 'bush':0.3}
    name_counter = 0
    leash_size = 4
    strike_speed = 2
    
    def __init__(self, position):
        name = 'ally_%s' % Ally.name_counter
        Ally.name_counter+=1
                
        DynamicObject.__init__(self, name, position)
        Unit.__init__(self, self.speed, self.hp, Corpse, 'good')
        Stalker.mixin(self, self.look_size)
        Striker.mixin(self, self.strike_speed, AllyBall, self.damage)
        Temporary.mixin(self, self.lifetime)
        
        self.stopped = False
        
        
        self.spawn()
    
    def handle_bind_master(self):
        self.fraction = self.master.fraction
    
    def update(self):
        if self.master:
            o_pos = self.master.position
            pos = self.position
            dist = abs(o_pos-pos)/TILESIZE
            if dist < self.leash_size:
                direct = self.hunt(False)
                if direct:
                    delta = random()*TILESIZE
                    direct += Point(delta, -delta)
                    self.strike_ball(direct)
                else:
                    Walker.update(self)
            else:
                self.move(o_pos - pos)
        else:
            Walker.update(self)
        
        Breakable.update(self)
        Temporary.update(self)
    
    

    
    def get_args(self):
        return Breakable.get_args(self)
    
    def handle_remove(self):
        if self.master:
            self.unbind_master()


class Cat(Walker, Solid, Stalker, DiplomacySubject, DynamicObject):
    speed = 20
    radius = TILESIZE
    rainbow_time = 30
    alive = True
    look_size = 300
    
    def __init__(self, name, position):
        DynamicObject.__init__(self, name, position)
        Solid.mixin(self, self.radius)
        Movable.mixin(self, self.speed)
        DiplomacySubject.mixin(self, 'good')
        self.heal_counter = 0
    
    def collission(self, player):
        if isinstance( player, Guided):
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
    



        

class Bat(Fighter, MetaMonster):
    hp = 3
    speed = 30
    damage = 1
    attack_speed = 1
    loot_cost = 10
    BLOCKTILES = ['stone', 'forest']
    SLOWTILES = {}
    
    def __init__(self, name, position):
        MetaMonster.__init__(self, name, position, self.speed, self.hp)
        Fighter.mixin(self)
    


class Zombie(Fighter, MetaMonster):
    hp = 20
    speed = 15
    damage = 2
    attack_speed = 0.5
    loot_cost = 30
    
    def __init__(self, name, position):
        MetaMonster.__init__(self, name, position, self.speed, self.hp)
        Fighter.mixin(self)
    

    

class Ghast(Fighter, MetaMonster):
    hp = 50
    speed = 10
    damage = 10
    attack_speed = 0.3
    loot_cost = 90
    
    def __init__(self, name, position):
        MetaMonster.__init__(self, name, position, self.speed, self.hp)
        Fighter.mixin(self)



class Lych(MetaMonster, Striker):
    hp = 25
    speed = 10
    damage = 5
    loot_cost = 60
    strike_speed = 1
    
    def __init__(self, name, position):
        MetaMonster.__init__(self, name, position, self.speed, self.hp)
        Striker.mixin(self, self.strike_speed, DarkBall, self.damage)
    
    def update(self):
        if self.alive:
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
                
        Breakable.update(self)
    

