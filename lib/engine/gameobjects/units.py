#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from server_logger import debug

from engine.enginelib.meta import *
from engine.mathlib import chance
from engine.enginelib.units_lib import *
from engine.gameobjects.items import *
from engine.gameobjects.shells import *
from engine.enginelib.mutable import MutableObject

from weakref import ProxyType

class Ally(Unit, Stalker, Temporary, Walker, Striker, GameObject, HierarchySubject):
    lifetime = 60
    player_hp = 60
    strike_speed = 3
    strike_impulse = 60

    speed = 40
    look_size = 10
    BLOCKTILES = ['stone', 'forest', ]
    SLOWTILES = {'water':0.5, 'bush':0.3}
    __leash_size = 4

    
    def __init__(self):   
        Unit.__init__(self, None, self.player_hp, self.speed, 'good')

        HierarchySubject.mixin(self)
        Stalker.mixin(self, self.look_size)
        Striker.mixin(self, self.strike_speed, self.strike_impulse)
        Temporary.mixin(self, self.lifetime)


        self.set_shell(AllyBall)
        self.set_brave()

    def set_leash(self, size):
        assert isinstance(size, int) and size>0

        self.__leash_size = size

    def update_leash(self, value):
        assert isinstance(value, int)

        new_leash - self.__leash_size+value
        if new_leash>0:
            self.__leash_size = new_leash

    
    def handle_bind_master(self, master):
        self.set_fraction(master.get_fraction())
        debug ('ally fraction', self.get_master().get_fraction(), self.get_fraction())
    
    def __update__(self, cur_time):
        if self.has_master():
            master_cord = self.get_master().cord
            self_cord = self.cord
            dist = abs(master_cord-self_cord)
            if dist < self.__leash_size:
                result = self.hunt()
                if result:
                    self.victim, vector = result
                    delta = random()*TILESIZE
                    vector += Position(delta, -delta)
                    self.strike_ball(vector)
                else:
                    self.move(self.get_walk_vector())
            else:
                self.move(master_cord.to_position() - self.position)
        else:
            self.move(self.get_walk_vector())
        
        super(Ally, self).__update__(cur_time)
    
    
    def get_args(self):
        return Breakable.get_args(self)
    
    def handle_remove(self):
        HierarchySubject.handle_remove(self)
        Unit.handle_remove(self)






class Cat(Walker, Solid, Stalker, DiplomacySubject, GameObject):
    speed = 20
    rainbow_time = 30
    look_size = 300
    heal_speed = 3
    
    def __init__(self):
        MutableObject.__init__(self, speed = self.speed)
        Solid.mixin(self)
        DiplomacySubject.mixin(self, 'neutral')
        self.prev_heal_time = time()
    
    def collission(self, player):
        if isinstance(player, Unit):
            if not self.is_enemy(player):
                cur_time = time()
                if cur_time - self.prev_heal_time > self.heal_speed:
                    self.prev_heal_time = cur_time
                    self.rainbow(player)
            
    
    def rainbow(self, player):
        player.heal(5)
        self.add_event('rainbow', self.rainbow_time)
    
    def __update__(self, cur_time):
        if chance(10):
            result = self.hunt(True)
            if result:
                victim, vector = result
                MutableObject.move(self, vector)
            else:
                self.move(self.get_walk_vector())
        else:
            if not self.get_vector():
                self.move(self.get_walk_vector())
        super(Cat, self).__update__(cur_time)
    



        

class Bat(MetaMonster):
    player_hp = 3
    speed = 30
    damage = 1
    attack_speed = 10
    loot_cost = 10
    BLOCKTILES = ['stone', 'forest']
    SLOWTILES = {}
    
    def __init__(self):
        MetaMonster.__init__(self, self.speed, self.player_hp)
    


class Zombie( MetaMonster):
    player_hp = 20
    speed = 15
    damage = 2
    attack_speed = 10
    loot_cost = 30
    
    def __init__(self):
        MetaMonster.__init__(self, self.speed, self.player_hp)
        

    def __update__(self, cur_time):
        super(Zombie, self).__update__(cur_time)
    

    

class Ghast( MetaMonster):
    player_hp = 50
    speed = 10
    damage = 10
    attack_speed = 30
    loot_cost = 90
    
    def __init__(self):
        MetaMonster.__init__(self, self.speed, self.player_hp)
        Fighter.mixin(self, self.damage, self.attack_speed)

    def __update__(self, cur_time):
        super(Ghast, self).__update__(cur_time)



class Lych(MetaMonster, Striker):
    player_hp = 25
    speed = 10
    damage = 5
    loot_cost = 60
    
    def __init__(self):
        MetaMonster.__init__(self, self.speed, self.player_hp)
        Striker.mixin(self, 1, self.damage)
        self.set_shell(DarkBall)
    
    def __update__(self, cur_time):
        if chance(50):
            result = self.hunt(False)
            if result:
                vector = result[1]
                delta = random()*TILESIZE
                vector += Position(delta, -delta)
                self.strike_ball(vector)
            else:
                self.move(self.get_walk_vector())
        else:
            self.move(self.get_walk_vector())
            
        super(Lych, self).__update__(cur_time)
        
