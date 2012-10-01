#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.engine_lib import *
from engine.mathlib import chance
from units_lib import *
from items import *
from movable import Movable
from skills import *
from map_observer import MapObserver


    

        
#####################################################################
class Player(Respawnable, Unit, MapObserver, Striker, Guided, Stats, Skill):
    "класс игрока"
    radius = TILESIZE/2
    prev_looked = set()
    speed = 40
    hp = 50
    BLOCKTILES = ['stone', 'forest', 'ocean']
    SLOWTILES = {'water':0.5, 'bush':0.3}
    damage = 2

    def __init__(self, name, player_position, look_size):
        GameObject.__init__(self, name, player_position)
        Unit.__init__(self, self.speed, self.hp, Corpse, self.name)
        MapObserver.__init__(self, look_size)
        Striker.__init__(self,2, Ball, self.damage)
        Respawnable.__init__(self, 10, 30)
        Stats.__init__(self)
        Skill.__init__(self)
        
    def handle_response(self):
        if not self.respawned:
            move_vector = Movable.handle_request(self)
            new_looked, observed, events, static_objects, static_events = self.look()
            messages = [('Look', (move_vector, new_looked, observed, events, static_objects, static_events))]
            if self.stats_changed:
                messages.append(self.get_stats())
    
            return messages
        else:
            return Respawnable.handle_response(self)
    
    @wrappers.action
    @wrappers.alive_only()
    def Strike(self, vector):
        self.strike_ball(vector)
    
    @wrappers.action
    @wrappers.alive_only()
    def Move(self, vector):
        Movable.move(self, vector)
    
    @wrappers.action
    def Look(self):
        return MapObserver.look(self)
    
    @wrappers.action
    def Skill(self):
        self.skill()
    

    
    #@wrappers.alive_only(Deadly)
    def update(self):
        Movable.update(self)
        Striker.update(self)
        Deadly.update(self)
        Stats.update(self)
    

##################################################################### 
from random import randrange       

class Walker(Movable):
    def update(self):
        x = randrange(-self.speed, self.speed)
        y = randrange(-self.speed, self.speed)
        direct = Point(x,y)
        self.move(direct)

class Cat(Walker, Solid, Stalker, GameObject):
    speed = 20
    radius = TILESIZE
    rainbow_time = 15
    alive = True
    look_size = 300
    def __init__(self, name, position):
        GameObject.__init__(self, name, position)
        Solid.__init__(self, self.radius)
        Movable.__init__(self, self.speed)
        self.heal_counter = 0
        self.rainbow_counter = 0
    
    @wrappers.player_filter(Guided)
    def collission(self, player):
        if self.heal_counter==0:
            self.rainbow(player)
        self.heal_counter+=1
        if self.heal_counter==10:
            self.heal_counter = 0
    
    def rainbow(self, player):
        player.heal(5)
        self.add_event(self.position, NullPoint, 'rainbow', [])
        self.rainbow_counter = self.rainbow_time
    
    def update(self):
        if self.rainbow_counter>0:
            self.add_event(self.position, NullPoint, 'rainbow', [])
            self.rainbow_counter-=1
        if chance(10):
            direct = self.hunt(True)
            Movable.move(self,direct)
        else:
            Walker.update(self)
    
    def complete_round(self):
        Movable.complete_round(self)

class MetaMonster(Respawnable, Lootable, Unit, Stalker, Walker):
    radius = TILESIZE
    look_size = 10
    BLOCKTILES = ['stone', 'forest', 'ocean']
    SLOWTILES = {'water':0.5, 'bush':0.3}
    def __init__(self, name, player_position, speed, hp):
        GameObject.__init__(self, name, player_position)
        Unit.__init__(self, speed, hp, Corpse, 'monsters')
        Stalker.__init__(self, self.look_size)
        Respawnable.__init__(self, 30, 60)
        
        self.stopped = False
        
        self.spawn()
    
    def hit(self, damage):
        self.stopped = 15
        Deadly.hit(self, damage)
    
    @wrappers.alive_only(Deadly)
    def update(self):
        if not self.stopped:
            if chance(50):
                direct = self.hunt(chance(50))
                if direct:
                    self.move(direct)
                else:
                    Walker.update(self)
            else:
                Walker.update(self)
        else:
            self.move(NullPoint)
            
            self.stopped-=1
        Movable.update(self)
        Deadly.update(self)
    
    def complete_round(self):
        Movable.complete_round(self)
        
    


class Zombie(Fighter, MetaMonster):
    hp = 50
    speed = 15
    damage = 1
    attack_speed = 10
    
    def __init__(self, name, position):
        MetaMonster.__init__(self, name, position, self.speed, self.hp)
        Fighter.__init__(self, self.damage, self.attack_speed)
    
    def complete_round(self):
        MetaMonster.complete_round(self)
        Fighter.complete_round(self)
    

class Ghast(Fighter, MetaMonster):
    hp = 30
    speed = 7
    damage = 5
    attack_speed = 30
    
    def __init__(self, name, position):
        MetaMonster.__init__(self, name, position, self.speed, self.hp)
        Fighter.__init__(self, self.damage, self.attack_speed)
    
    def complete_round(self):
        MetaMonster.complete_round(self)
        Fighter.complete_round(self)


class Lych(MetaMonster, Striker):
    hp = 5
    speed = 15
    damage = 2
    
    def __init__(self, name, position):
        MetaMonster.__init__(self, name, position, self.speed, self.hp)
        Striker.__init__(self, 10, DarkBall, self.damage)
    
    @wrappers.alive_only(Deadly)
    def update(self):
        direct = self.hunt(False)
        if direct:
            if chance(50):
                delta = randrange(-TILESIZE, TILESIZE)
                direct += Point(delta, -delta)
            self.strike_ball(direct)
        else:
            Walker.update(self)
            
        Movable.update(self)
        Striker.update(self)
        Deadly.update(self)
    
    def complete_round(self):
        Movable.complete_round(self)
        Striker.complete_round(self)
