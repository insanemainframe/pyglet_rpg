#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.engine_lib import *
from engine.mathlib import chance
from engine.gameobjects.items import *
from engine.gameobjects.movable import Movable


from random import randrange, random      


class Unit(Solid, Movable, Deadly, DiplomacySubject, GameObject):
    def __init__(self, speed, hp, corpse, fraction):
        Movable.__init__(self, speed)
        Deadly.__init__(self, corpse, hp)
        DiplomacySubject.__init__(self, fraction)

class Lootable(Deadly):
    loot = [Cloak] #Sceptre, HealPotion, Sword, Armor, Sceptre, SpeedPotion, Gold, Cloak]
    
    def die(self):
        if chance(60):
            item = choice(self.loot)(self.position)
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
                self.add_event('attack', ())
    
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
        if game.guided_players:
            players = self.get_location().get_players().values()
            dists = []
            for player in players:
                if player.fraction!=self.fraction and  player.fraction!='good':
                    if not player.invisible:
                        dists.append(player.position - self.position)
            if dists:
                victim = min(dists, key = lambda vector: abs(vector))
                return victim
            else:
                return NullPoint
            
class Striker:
    def __init__(self, strike_speed, shell, damage):
        self.strike_shell = shell
        self.strike_counter = 0
        self.strike_speed = strike_speed
        self.damage = damage
    
    @wrappers.alive_only()
    def strike_ball(self, vector):
        if self.strike_counter==0 and vector:
            ball_name = 'ball%s' % game.ball_counter
            game.ball_counter+=1
            ball = self.strike_shell(ball_name, self.position, vector, self.fraction, self.name, self.damage)
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
        positivex = -1 if random()>0.5 else 1
        positivey = -1 if random()>0.5 else 1
        partx = random()*10
        party = random()*10
        x = positivex*self.speed*partx
        y = positivey*self.speed*party
        direct = Point(x,y)
        self.move(direct)
