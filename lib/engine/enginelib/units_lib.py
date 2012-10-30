#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.enginelib.meta import *
from engine.mathlib import chance
from engine.gameobjects.items import *
from engine.enginelib.movable import Movable
from engine.enginelib import wrappers



from random import randrange, random      


class Unit(Solid, Movable, Deadly, DiplomacySubject, GameObject):
    def __init__(self, speed, hp, corpse, fraction):
        Movable.__init__(self, speed)
        Deadly.__init__(self, corpse, hp)
        DiplomacySubject.__init__(self, fraction)
        Solid.__init__(self, TILESIZE/2)

class Lootable(Deadly):
    loot = [Lamp, Sceptre, HealPotion, Sword, Armor, Sceptre, SpeedPotion, Gold, Cloak]
    def __init__(self, cost):
        self.cost = cost if cost<= 100 else 50
    
    def die(self):
        if chance(self.cost):
            item = choice(self.loot)(self.position)
            self.world.new_object(item)
        Deadly.die(self)

class Fighter:
    def __init__(self, damage, attack_speed=5):
        self.attack_speed = attack_speed
        self.attack_counter = 0
        self.damage = damage
    
    @wrappers.alive_only()
    @wrappers.player_filter(Deadly)
    def collission(self, player):
        if self.fraction!=player.fraction:
            if self.attack_counter==0:
                player.hit(self.damage)
                self.add_event('attack')
    
    def complete_round(self):
        if self.attack_counter < self.attack_speed:
            self.attack_counter+=1
        else:
            self.attack_counter=0

class Stalker:
    "объекты охотящиеся за игроками"
    def __init__(self, look_size):
        self.look_size = look_size
    
    def hunt(self, inradius = False):
            players = self.location.get_players_list()
            dists = []
            for player in players:
                if player.fraction!=self.fraction and  player.fraction!='good':
                    if not player.invisible:
                        dists.append(player.position - self.position)
            if dists:
                victim = min(dists, key = abs)
                return victim
            else:
                return Point(0,0)
            
class Striker:
    def __init__(self, strike_speed, shell, damage):
        self.strike_shell = shell
        self.strike_counter = 0
        self.strike_speed = strike_speed
        self.damage = damage
    
    @wrappers.alive_only()
    def strike_ball(self, vector):
        if self.strike_counter==0 and vector:
            ball = self.strike_shell(self.position, vector, self.fraction, self.name, self.damage)
            self.world.new_object(ball)
            self.strike_counter+=self.strike_speed
    
    def plus_damage(self, damage):
        self.damage+=damage
            
    def update(self):
        if self.strike_counter>0:
            self.strike_counter -=1
    
    def complete_round(self):
        self.striked = False

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
        self.world.game.guided_changed = True
    
    def update(self):
        stats = (self.hp, self.hp_value, self.speed, self.damage,
            self.gold, self.kills, self.death_counter, self.skills, bool(self.invisible))
        if self.prev_stats!=stats:
            self.prev_stats = stats
            self.stats_changed = True
    
    def get_stats(self):
        data = (self.hp, self.hp_value, self.speed, self.damage,
                self.gold, self.kills, self.death_counter ,self.skills, bool(self.invisible))
        self.stats_changed = False
        return data


class Walker(Movable):
    def update(self):
        positive_x = -1 if random()>0.5 else 1
        positive_y = -1 if random()>0.5 else 1
        partx = random()*10
        party = random()*10
        x = positive_x*self.speed*partx
        y = positive_y*self.speed*party
        direct = Point(x,y)
        self.move(direct)


class MetaMonster(Respawnable, Lootable, Unit, Stalker, Walker, DynamicObject):
    radius = TILESIZE
    look_size = 10
    BLOCKTILES = ['stone', 'forest', 'ocean', 'lava']
    SLOWTILES = {'water':0.5, 'bush':0.3}
    def __init__(self, name, position, speed, hp):
        DynamicObject.__init__(self, name, position)
        Unit.__init__(self, speed, hp, Corpse, 'monsters')
        Stalker.__init__(self, self.look_size)
        Respawnable.__init__(self, 60, 100)
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
