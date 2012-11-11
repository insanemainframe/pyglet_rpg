#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.enginelib.meta import *
from engine.mathlib import chance
from engine.enginelib.units_lib import *
from engine.gameobjects.items import *
from engine.gameobjects.shells import *
from engine.enginelib.mutable import MutableObject

from weakref import ProxyType

class Ally(Unit, Stalker, Temporary, Walker, Striker, GameObject, HierarchySubject):
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
    
    def __init__(self):   
        Unit.__init__(self, None, self.hp, self.speed, 'good')

        HierarchySubject.mixin(self)
        Stalker.mixin(self, self.look_size)
        Striker.mixin(self, 10, self.damage)
        Temporary.mixin(self, self.lifetime)


        self.set_shell(AllyBall)

        self.spawn()
    
    def handle_bind_master(self):
        self.fraction = self.master.fraction
    
    def update(self):
        assert self.master is None or isinstance(self.master, ProxyType)

        if self.master:
            o_pos = self.master.position
            pos = self.position
            dist = abs(o_pos-pos)/TILESIZE
            if dist < self.leash_size:
                result = self.hunt()
                if result:
                    self.victim, vector = result
                    delta = random()*TILESIZE
                    vector += Position(delta, -delta)
                    self.strike_ball(vector)
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



    def verify_chunk(self, location, chunk):
        print ('ally verify_chunk')
        if chunk==self.master.chunk:
            return True
        for chunk in chunk.get_nears():
            if chunk==self.master.chunk:
                return True
        return False



class Cat(Walker, Solid, Stalker, DiplomacySubject, GameObject):
    speed = 20
    radius = TILESIZE
    rainbow_time = 30
    look_size = 300
    heal_speed = 3
    
    def __init__(self):
        MutableObject.__init__(self, speed = self.speed)
        Solid.mixin(self, self.radius)
        DiplomacySubject.mixin(self, 'good')
        self.prev_heal_time = time()
    
    def collission(self, player):
        if isinstance( player, Guided):
            cur_time = time()
            if cur_time - self.prev_heal_time > self.heal_speed:
                self.prev_heal_time = cur_time
                self.rainbow(player)
            
    
    def rainbow(self, player):
        player.heal(5)
        self.add_event('rainbow', self.rainbow_time)
    
    def update(self):
        if chance(10):
            direct = self.hunt(True)
            MutableObject.move(self.direct)
        else:
            if not self.vector:
                Walker.update(self)
    



        

class Bat(Fighter, MetaMonster):
    hp = 3
    speed = 30
    damage = 1
    attack_speed = 10
    loot_cost = 10
    BLOCKTILES = ['stone', 'forest']
    SLOWTILES = {}
    
    def __init__(self):
        MetaMonster.__init__(self, self.speed, self.hp)
        Fighter.mixin(self, self.damage, self.attack_speed)
    


class Zombie(Fighter, MetaMonster):
    hp = 20
    speed = 15
    damage = 2
    attack_speed = 10
    loot_cost = 30
    
    def __init__(self):
        MetaMonster.__init__(self, self.speed, self.hp)
        Fighter.mixin(self, self.damage, self.attack_speed)
    

    

class Ghast(Fighter, MetaMonster):
    hp = 50
    speed = 10
    damage = 10
    attack_speed = 30
    loot_cost = 90
    
    def __init__(self):
        MetaMonster.__init__(self, self.speed, self.hp)
        Fighter.mixin(self, self.damage, self.attack_speed)



class Lych(MetaMonster, Striker):
    hp = 25
    speed = 10
    damage = 5
    loot_cost = 60
    
    def __init__(self):
        MetaMonster.__init__(self, self.speed, self.hp)
        Striker.mixin(self, 10, self.damage)
        self.set_shell(DarkBall)
    
    def update(self):
        if chance(50):
            result = self.hunt(False)
            if result:
                vector = result[1]
                delta = random()*TILESIZE
                vector += Position(delta, -delta)
                self.strike_ball(vector)
            else:
                Walker.update(self)
        else:
            Walker.update(self)
            
        Breakable.update(self)
        
