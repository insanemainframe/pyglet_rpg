#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.enginelib.meta import *
from engine.mathlib import Cord, Position, ChunkCord,  chance
from engine.gameobjects.items import *
from engine.enginelib.mutable import MutableObject
from engine.gameobjects.shells import Ball



from random import randrange, random, choice    
from math import hypot
from weakref import ProxyType
from time import time

class Corpse(GameObject, Temporary):
    "кости остающиеся после смерти живых игроков"
    def mixin(self):
        GameObject.__init__(self)
        Temporary.mixin(self, 5)
    
    def update(self):
        GameObject.update(self)
        Temporary.update(self)


class Unit(MutableObject, Solid, Breakable, DiplomacySubject):
    def __init__(self, name, hp, speed, fraction):
        MutableObject.__init__(self, name, speed)
        Breakable.mixin(self, hp)
        DiplomacySubject.mixin(self, fraction)
        Solid.mixin(self, TILESIZE/2)

        self.set_corpse(Corpse)

    def verify_chunk(self, location, chunk):
        for player in chunk.get_list(Unit):
            if player.fraction!=self.fraction and player.fraction!='good':
                return False
        return True

    def verify_position(self, location, chunk, voxel, ci ,cj):
        # print ('unit verify_position')
        for player in sum(voxel.get_nears(), []):
            if isinstance(player, Solid):
                return False

        return True


class Lootable:
    "объект, послесмерти которого выпадает предмет"
    loot = [Lamp, Sceptre, HealPotion, Sword, Armor, Sceptre, SpeedPotion, Gold, Cloak]
    def mixin(self, cost):
        if TEST_MODE:
            cost = 100
            self.loot = [Lamp]
        self.cost = cost if cost<= 100 else 50

    
    def handle_remove(self):
        if chance(self.cost):
            item = choice(self.loot)()
            self.location.new_object(item, position = self.position)


class Fighter:
    "объект спобоный на ближнюю атаку"
    atack_distance = int(hypot(1.5, 1.5))
    def mixin(self, damage, attack_speed=30):
        self.attack_speed = attack_speed
        self.damage = damage

        self.prev_attack_time = time()

    def fight_all(self):
        cur_time = time()
        if cur_time - self.prev_attack_time > self.attack_speed:
            self.prev_attack_time = cur_time
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
                            break

    def fight(self, player, vector):
        cur_time = time()
        if cur_time - self.prev_attack_time > self.attack_speed:
            self.prev_attack_time = cur_time
            if abs(vector)<=self.atack_distance:
                    player.hit(self.damage)
                    self.add_event('attack')


    





class Stalker:
    "объекты охотящиеся за игроками"
    def mixin(self, look_size):
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
    "дает возможность игроку стрелять снарядами"
    default_shell = Ball
    def mixin(self, strike_speed = 1, damage = 1):
        self.shell_type = None
        self.shell_type = Striker.default_shell
        self.strike_speed = strike_speed
        self.damage = damage

        self.prev_strike_time = time()

    def set_shell(self, shell_type):
        self.shell_type = shell_type

    def set_strike_speed(self, strike_speed):
        self.strike_speed = strike_speed
    
    def strike_ball(self, vector):
        assert isinstance(vector, Position)
        cur_time = time()

        if cur_time-self.prev_strike_time>1.0/self.strike_speed:
            self.prev_strike_time = cur_time

            ball = self.shell_type(vector, self.fraction, proxy(self), self.damage)
            self.location.new_object(ball, position = self.position)
    
    def plus_damage(self, damage):
        self.damage+=damage
            

    


class Stats:
    def mixin(self):
        self.gold = 0
        self.kills = 0
        self.prev_stats = None
    
    def plus_gold(self, gold=1):
        self.gold+=1
    
    def plus_kills(self):
        self.kills+=1
        self.location.game.guided_changed = True
    
    def is_stats_changed(self):
        stats = (self.hp, self.hp_value, self.speed, self.damage,
            self.gold, self.kills, self.death_counter, self.skills, bool(self.invisible))
        
        if self.prev_stats!=stats:
            self.prev_stats = stats
            return True
        return False
    
    def get_stats(self):
        data = (self.hp, self.hp_value, self.speed, self.damage,
                self.gold, self.kills, self.death_counter ,self.skills, bool(self.invisible))
        self.stats_changed = False
        return data


class Walker(MutableObject):
    def update(self):
        positive_x = -1 if random()>0.5 else 1
        positive_y = -1 if random()>0.5 else 1
        partx = random()*10
        party = random()*10
        x = positive_x*self.speed*partx
        y = positive_y*self.speed*party
        direct = Position(x,y)
        self.move(direct)


class MetaMonster(Respawnable, Lootable, Unit, Stalker, Walker, SavableRandom):
    radius = TILESIZE
    look_size = 10
    BLOCKTILES = ['stone', 'forest', 'ocean', 'lava']
    SLOWTILES = {'water':0.5, 'bush':0.3}
    fraction = 'monsters'
    
    def __init__(self, speed, hp):
        Unit.__init__(self, None, hp, speed, self.fraction)

        Stalker.mixin(self, self.look_size)
        Respawnable.mixin(self, 60, 100)
        Lootable.mixin(self, self.loot_cost)
        
        self.stopped = False
        
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


        Breakable.update(self)
    
    def get_args(self):
        return Breakable.get_args(self)
    


    def __save__(self):
        return []

    @classmethod
    def __load__(cls, location):
        return cls()
