#!/usr/bin/env python
# -*- coding: utf-8 -*-
from engine.engine_lib import *
from engine.mathlib import chance
from items import *
from movable import Movable

from config import *


class Unit(Solid, Movable, Deadly, DiplomacySubject):
    def __init__(self, speed, hp, corpse, fraction):
        Movable.__init__(self, speed)
        Deadly.__init__(self, corpse, hp)
        DiplomacySubject.__init__(self, fraction)

class Lootable(Deadly):
    loot = [HealPotion, Sword, Armor, Sceptre, SpeedPotion, Gold]
    
    def die(self):
        if chance(30):
            item = choice(self.loot)(self.position)
            game.new_object(item)
        Deadly.die(self)

class Fighter:
    def __init__(self, damage, attack_speed=10):
        self.attack_speed = attack_speed
        self.attack_counter = 0
        self.damage = damage
    
    @wrappers.alive_only()
    @wrappers.player_filter(Deadly)
    def collission(self, player):
        if self.fraction!=player.fraction:
            if self.attack_counter==0:
                player.hit(self.damage)
                self.add_event(self.position, NullPoint, 'attack', [])
    
    def complete_round(self):
        if self.attack_counter < self.attack_speed:
            self.attack_counter+=1
        else:
            self.attack_counter=0
    
    
class Stats:
    def __init__(self):
        self.gold = 0
        self.kills = 0
        self.stats_changed = False
        self.prev_stats = None
    
    def plus_gold(self, gold=1):
        self.gold+=1
    
    def plus_kills(self):
        self.kills+=1
    
    def update(self):
        stats = (self.hp, self.hp_value, self.speed, self.damage, self.gold, self.kills, self.death_counter)
        if self.prev_stats!=stats:
            self.prev_stats = stats
            self.stats_changed = True
    
    def get_stats(self):
        data = (self.hp, self.hp_value, self.speed, self.damage, self.gold, self.kills, self.death_counter)
        self.stats_changed = False
        return ('PlayerStats', data)
    

        
#####################################################################
class Player(Respawnable, Unit, MapObserver, Striker, Guided, Stats):
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
    
    @wrappers.alive_only()
    def handle_action(self, action, args):
        GameObject.handle_action(self,action,args)
        
    def handle_response(self):
        if not self.respawned:
            move_vector = Movable.handle_request(self)
            new_looked, observed, updates = self.look()
            messages = [('Look', (move_vector, new_looked, observed, updates, []))]
            if self.stats_changed:
                messages.append(self.get_stats())
    
            return messages
        else:
            return Respawnable.handle_response(self)

    @wrappers.alive_only()
    def Strike(self, vector):
        self.strike_ball(vector)
    
    @wrappers.alive_only()
    def Move(self, vector):
        print 'player/move'
        Movable.move(self, vector)
    
    def Look(self):
        return MapObserver.look(self)
    
    def complete_round(self):
        Movable.complete_round(self)
        Striker.complete_round(self)
    
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
        self.spawn()
    
    @wrappers.alive_only(Deadly)
    def update(self):
        direct = self.hunt(chance(50))
            
        if direct:
            self.move(direct)
        else:
            Walker.update(self)
        Movable.update(self)
        Deadly.update(self)
    
    def complete_round(self):
        Movable.complete_round(self)
        
    


class Zombie(Fighter, MetaMonster):
    hp = 3
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
    hp = 20
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
        direct = self.hunt()
        if direct:
            self.strike_ball(direct)
        else:
            Walker.update(self)
            
        Movable.update(self)
        Striker.update(self)
        Deadly.update(self)
    
    def complete_round(self):
        Movable.complete_round(self)
        Striker.complete_round(self)
