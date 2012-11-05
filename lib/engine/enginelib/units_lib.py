#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.enginelib.meta import *
from engine.mathlib import chance
from engine.gameobjects.items import *
from engine.enginelib.movable import Movable



from random import randrange, random, choice    
from math import hypot
from weakref import ProxyType

class Unit(Solid, Movable, Breakable, DiplomacySubject, Updatable, GameObject):
    def __init__(self, speed, hp, corpse, fraction):
        Updatable.__init__(self)
        Movable.__init__(self, speed)
        Breakable.__init__(self, hp, corpse)
        DiplomacySubject.__init__(self, fraction)
        Solid.__init__(self, TILESIZE/2)

    @classmethod
    def verify_chunk(cls, location, chunk):
        for player in chunk.get_list(Unit):
            if player.fraction!=cls.fraction and player.fraction!='good':
                return False
        return True

    @classmethod
    def verify_position(cls, location, chunk, ci ,cj):
        print ('unit verify_position')
        if not GameObject.verify_position(location, chunk, ci ,cj):
            return False

        for i,j in location.get_near_cords(ci ,cj) + [(ci ,cj)]:
                for player in location.get_voxel(i,j):
                    if isinstance(player, Solid):
                        return False

        return True


class Lootable(Breakable):
    loot = [Lamp, Sceptre, HealPotion, Sword, Armor, Sceptre, SpeedPotion, Gold, Cloak]
    def __init__(self, cost):
        if TEST_MODE:
            cost = 100
            self.loot = [Lamp]
        self.cost = cost if cost<= 100 else 50

    
    def die(self):
        if chance(self.cost):
            item = choice(self.loot)()
            self.location.new_object(item, position = self.position)
        Breakable.die(self)


class Fighter:
    atack_distance = int(hypot(1.5, 1.5))
    def __init__(self, damage, attack_speed=30):
        self.attack_speed = attack_speed
        self.attack_counter = 0
        self.damage = damage

    def fight_all(self):
        if self.attack_counter==0:
            for i,j in self.location.get_near_cords(*self.cord.get()):
                tile = self.location.get_voxel(i,j)
                for player in tile:
                    if isinstance(player, Unit):
                        
                        enemy = self.fraction!=player.fraction

                        in_distance = self.cord.in_radius(player.cord, self.atack_distance)

                        if enemy and in_distance:
                            print ('fight')
                            player.hit(self.damage)
                            self.add_event('attack')
                            self.attack_counter = self.attack_speed
                            break

    def fight(self, player, vector):
        if abs(vector)<=self.atack_distance:
            if self.attack_counter==0:
                player.hit(self.damage)
                self.add_event('attack')
                self.attack_counter = self.attack_speed


    
    def complete_round(self):
        if self.attack_counter > 0:
            self.attack_counter-=1




class Stalker:
    "объекты охотящиеся за игроками"
    def __init__(self, look_size):
        self.look_size = look_size
    
    def hunt(self, inradius = False):
            players = self.chunk.get_list_all(Unit)
            if players:
                dists = []
                for player in players:
                    fraction = player.fraction
                    not_self = player.name!=self.name
                    is_enemy = not (fraction is self.fraction or fraction is 'good')

                    if not_self and is_enemy:
                        if not player.invisible:
                            dists.append((player, player.position - self.position))
                if dists:
                    victim, vector = min(dists, key = lambda pair: abs(pair[1]))
                    assert isinstance(victim, ProxyType)
                    return victim, vector
                else:
                    return False
            return False
            
class Striker:
    def __init__(self, strike_speed, shell, damage):
        self.strike_shell = shell
        self.strike_counter = 0
        self.strike_speed = strike_speed
        self.damage = damage
    
    def strike_ball(self, vector):
        if self.strike_counter==0 and vector:
            ball = self.strike_shell(vector, self.fraction, proxy(self), self.damage)
            self.location.new_object(ball, position = self.position)
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
        self.location.game.guided_changed = True
    
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


class MetaMonster(Respawnable, Lootable, Unit, Stalker, Walker, GameObject, Savable):
    radius = TILESIZE
    look_size = 10
    BLOCKTILES = ['stone', 'forest', 'ocean', 'lava']
    SLOWTILES = {'water':0.5, 'bush':0.3}
    fraction = 'monsters'
    
    def __init__(self, speed, hp):
        GameObject.__init__(self)
        Unit.__init__(self, speed, hp, Corpse, self.fraction)
        Stalker.__init__(self, self.look_size)
        Respawnable.__init__(self, 60, 100)
        Lootable.__init__(self, self.loot_cost)
        
        self.stopped = False
        
        self.spawn()
        self.hunting = False
        self.victim = None
        self.is_blocked = False
    
    def hit(self, damage):
        self.stop(10)
        Breakable.hit(self, damage)
    
    def update(self):
        victim_trig = self.victim and self.victim.position_changed

        if self.is_blocked or chance(10):
            self.hunting = False
            Walker.update(self)
            self.is_blocked = False
        else:
            if victim_trig or not self.hunting:
                result = self.hunt()
                if result:
                    self.victim, self.vector_to_victim = result
                    self.hunting = True
                    
            if self.hunting:
                if abs(self.vector_to_victim)<=TILESIZE*2:
                    self.fight(self.victim, self.vector_to_victim)
                else:
                    self.is_blocked = not self.move(self.vector_to_victim)
            else:
                Walker.update(self)


        Movable.update(self)
        Breakable.update(self)
    
    def get_args(self):
        return Breakable.get_args(self)
    
    def complete_round(self):
        Movable.complete_round(self)

    def __save__(self):
        return []

    @staticmethod
    def __load__():
        return []

