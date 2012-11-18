#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from server_logger import debug

from engine.enginelib.meta import *
from engine.mathlib import Cord, Position, ChunkCord,  chance
from engine.gameobjects.items import *
from engine.enginelib.mutable import MutableObject
from engine.gameobjects.shells import Ball



from random import randrange, random, choice    
from math import hypot
from weakref import ProxyType, ReferenceError
from time import time

class Corpse(GameObject, Temporary):
    "кости остающиеся после смерти живых игроков"
    def __init__(self):
        GameObject.__init__(self)
        Temporary.mixin(self, 5)
    
    def update(self):
        Temporary.update(self)


class Unit(MutableObject, Solid, Breakable, DiplomacySubject):
    __brave = False

    def __init__(self, name, hp, speed, fraction):
        MutableObject.__init__(self, name)
        Breakable.mixin(self, hp)
        DiplomacySubject.mixin(self, fraction)
        Solid.mixin(self)

        self.set_speed(speed)

        self.set_corpse(Corpse)

    def verify_chunk(self, location, chunk):
        if not self.__brave:
            for player in chunk.get_list(Unit):
                if self.is_enemy(player):
                    return False
        return True

    def verify_position(self, location, chunk, cord, generation = True):
        if not GameObject.verify_position(self, location, chunk, cord, generation):
            return False
            
        for player in sum(location.get_near_voxels(cord), []):
            if isinstance(player, Solid):
                return False

        return True

    def set_brave(self):
        self.__brave = True

    def handle_remove(self):
        Breakable.handle_remove(self)


class Lootable:
    "объект, послесмерти которого выпадает предмет"
    __loot = set((Lamp, Sceptre, HealPotion, Sword, Armor, Sceptre, SpeedPotion, Gold, Cloak))
    def mixin(self, cost):
        if TEST_MODE:
            cost = 100
            self.__loot = set((Lamp,))
        self.cost = cost if cost<= 100 else 50

    def add_loot(self, loot_type):
        assert isinstance(loot_type, type)
        self.__loot.add(loot_type)

    
    def handle_remove(self):
        if chance(self.cost):
            item = choice(list(self.__loot))()
            self.location.new_object(item, position = self.position)


class Fighter:
    "объект спобоный на ближнюю атаку"
    atack_distance = int(hypot(1.5, 1.5))
    def mixin(self, damage, attack_speed=30):
        self.__speed = attack_speed
        self.__damage = damage

        self.__prev_time = time()

    def set_damage(self, damage):
        self.__damage = damage

    def update_damage(self, damage):
        
        self.__damage+=damage

    def fight_all(self):
        cur_time = time()
        if cur_time - self.__prev_time > self.__speed:
            self.__prev_time = cur_time
            for i,j in self.location.get_near_cords(*self.cord.get()):
                tile = self.location.get_voxel(i,j)
                for player in tile:
                    if isinstance(player, Unit):
                        
                        in_distance = self.cord.in_radius(player.cord, self.atack_distance)

                        if self.is_enemy(player) and in_distance:
                            debug ('fight')
                            player.hit(self.__damage)
                            self.add_event('attack')
                            break

    def fight(self, player, vector):
        cur_time = time()
        if cur_time - self.__prev_time > self.__speed:
            self.__prev_time = cur_time
            if abs(vector)<=self.atack_distance:
                    player.hit(self.__damage)
                    self.add_event('attack')


    





class Stalker:
    "объекты охотящиеся за игроками"
    def mixin(self, look_size):
        self.__look_size = look_size
    
    def hunt(self, inradius = False):
            players = self.chunk.get_list_all(Unit)
            if players:
                dists = []
                for player in players:
                    if self.is_enemy(player):
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
    def mixin(self, strike_speed = 1, impact = 1):
        self.__speed = strike_speed
        self.__impact = impact

        self.__prev_time = time()


    def set_shell(self, shell_type):
        self.__shell_type = shell_type

    def update_strike_speed(self, plus):
        self.__speed +=plus

    def set_strike_speed(self, strike_speed):
        assert strike_speed>0
        self.__speed = strike_speed

    def set_strike_impact(self, impact):
        assert impact>0
        self.__impact = impact

    def update_strike_impact(self, value):
        new_impact = self.__impact + value

        assert new_impact>0
        self.__impact = new_impact
    
    def strike_ball(self, vector):
        assert isinstance(vector, Position)
        if vector:
            cur_time = time()

            if cur_time-self.__prev_time>1.0/self.__speed:
                self.__prev_time = cur_time

                ball = self.__shell_type(vector, self.__impact, proxy(self))

                self.location.new_object(ball, position = self.position)
    

            

    


class Stats:
    def mixin(self):
        self.gold = 0
        self.kills = 0
        self.prev_stats = None
    
    def plus_gold(self, gold=1):
        self.gold+=1
    
    def plus_kills(self):
        self.kills+=1
        self.location.change_guided()


    
    def is_stats_changed(self):
        stats = (self.get_hp_value(), self.get_hp(), self.speed, 0,
            self.gold, self.kills, self.death_counter, self.skills, self.is_spy())
        
        if self.prev_stats!=stats:
            self.prev_stats = stats
            return True
        return False
    
    def get_stats(self):
        data = (self.get_hp_value(), self.get_hp(), self.speed, 0,
                self.gold, self.kills, self.death_counter ,self.skills, self.is_spy())
        self.stats_changed = False
        return data


class Walker(MutableObject):
    def get_walk_vector(self):
        positive_x = -1 if random()>0.5 else 1
        positive_y = -1 if random()>0.5 else 1
        partx = random()*10
        party = random()*10
        x = positive_x*self.speed*partx
        y = positive_y*self.speed*party
        direct = Position(x,y)
        return direct


class MetaMonster(Respawnable, Lootable, Unit, Stalker, Walker, SavableRandom):
    radius = TILESIZE
    look_size = 10
    BLOCKTILES = ['stone', 'forest', 'ocean', 'lava']
    SLOWTILES = {'water':0.5, 'bush':0.3}
    __fraction = 'bad'
    
    def __init__(self, speed, hp):
        Unit.__init__(self, None, hp, speed, self.__fraction)

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
        try:
            victim_trig = self.victim and self.victim.position_changed

        except ReferenceError:
            pass
        else:
            if self.is_blocked or chance(10):
                self.hunting = False
                self.move(self.get_walk_vector())
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
                    self.move(self.get_walk_vector())

        finally:
            Breakable.update(self)
    
    def get_args(self):
        return Breakable.get_args(self)


    def verify_chunk(self, location, chunk):
        if chunk.cord==location.main_chunk.cord:
            return False
        return Unit.verify_chunk(self, location, chunk)


    def handle_remove(self):
        Unit.handle_remove(self)
        Lootable.handle_remove(self)
    


    def __save__(self):
        return []

    @classmethod
    def __load__(cls, location):
        return cls()
