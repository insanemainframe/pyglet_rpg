#!/usr/bin/env python
# -*- coding: utf-8 -*-
from share.mathlib import *
from share.map import *
from mathlib import *
import game

#

class UnknownAction(Exception):
    pass


class ActionDenied(Exception):
    pass

class ActionError(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return 'ActionError: %s' % self.message

class wrappers:
    @staticmethod
    def alive_only(Class=None):
        def wrapper(method):
            def wrap(self,*args):
                if self.alive:
                    return method(self, *args)
                else:
                    #print '%s mot alive' % self.name
                    if Class:
                        return getattr(Class, method.__name__)(self, *args)
            return wrap
        return wrapper
    
    @staticmethod
    def player_filter(Class):
        def wrapper(method):
            def wrap(self, player):
                if isinstance(player, Class):
                    return method(self,player)
            return wrap
        return wrapper
    @staticmethod
    def player_filter_alive(method):
        def wrap(self, player):
            if player.alive:
                return method(self,player)
        return wrap
    
    


#####################################################################
class GameObject:
    def __init__(self, name, position):
        self.name = name
        self._position = position
        self._prev_position = position
        self.REMOVE = False            
        self.alive = True
    
    @property
    def position(self):
        return self._position
    
    @position.setter
    def position_set(self, position):
        self._prev_position = self._position
        self._position  = position
    
    
    def handle_action(self, action, args):
        if hasattr(self, action):
            return getattr(self, action)(*args)
        else:
            raise ActionError('no action %s' % action)
    
    def update(self):
        pass
    
    def collission(self, player):
        pass
        
    def tile_collission(self, tile):
        pass
    
    def add_event(self, *args):
        game.add_event(self.name, *args)
    
    
    def remove(self):
        return True
    
    def handle_response(self):
        return []

#####################################################################
class StaticObject(GameObject):
    def __init__(self, name, position):
        GameObject.__init__(self, name, position)
    
    def update(self):
        self.add_event(self.position, NullPoint, 'exist', [])

    
    def complete_round(self):
        pass




class Guided(GameObject):
    "управляемый игроком объекта"
    pass

class Solid(GameObject):
    def __init__(self, radius):
        self.radius = radius
    
    def collission(self, player):
        pass

#####################################################################

class MapObserver(MapTools):
    "класс объекта видящего карту"
    prev_looked = set()
    prev_observed = set()
    def __init__(self, look_size):
        MapTools.__init__(self, game.size, game.size)
        self.look_size = look_size
    def look(self):
        "возвращает список координат видимых клеток из позиции position, с координаами относительно начала карты"
        position = self.position
        rad = self.look_size
        I,J = (position/TILESIZE).get()
        #
        new_updates = {}
        #
        observed = set()
        looked = set()
        for i in xrange(I-rad, I+rad):
            for j in xrange(J-rad, J+rad):
                diff = hypot(I-i,J-j) - rad
                if diff<0:
                    i,j = self.resize(i), self.resize(j)
                    try:
                        tile_type = game.world.map[i][j]
                    except IndexError, excp:
                        pass
                    else:
                        looked.add((Point(i,j), tile_type))
                        observed.add((i,j))
                        if (i,j) in game.events:
                            for uid, (name, object_type, position, action, args) in game.events[(i,j)]:
                                if name==self.name:
                                    object_type = 'Self'
                                new_updates[uid] = (name, object_type, position, action, args)

        new_looked = looked - self.prev_looked
        self.prev_looked = looked
        self.prev_observed = observed
        return new_looked, observed, new_updates
    

####################################################################

class Stalker:
    "объекты охотящиеся за игроками"
    def __init__(self, look_size):
        self.look_size = look_size
    
    def hunt(self, inradius = False):
        for player in game.players.values():
            if isinstance(player, Guided) and player.alive:
                distance = player.position - self.position
                if inradius:
                    if abs(distance/TILESIZE)<self.look_size:
                        return player.position - self.position
                else:
                    return player.position - self.position
        return None
        
class Deadly:
    "класс для живых объектов"
    def __init__(self, corpse, hp, heal_speed=0.01, death_time=20):
        self.hp_value = hp
        self.heal_speed = heal_speed
        self.death_time = death_time
        self.death_time_value = death_time
        self.corpse = corpse
        self.death_counter = 0
        self.spawn()
    
    def spawn(self):
        self.alive = True
        self.hp = self.hp_value
        
    

    
    def hit(self, hp):
        if self.alive:
            self.hp-=hp
            if self.hp<=0:
                self.die()
                self.hp = self.hp_value
                return True
            else:
                return False
        else:
            return False
    
    def heal(self, hp):
        new_hp = self.hp+ hp
        if new_hp>self.hp_value:
            new_hp = self.hp_value
        
        self.hp = new_hp
    
    def plus_hp(self, armor):
        self.hp_value+=armor
    
    def update(self):
        if self.alive:
            if self.hp<self.hp_value:
                self.hp+=self.heal_speed
        else:
            if self.death_time>0:
                self.death_time-=1
                self.add_event(self.position, NullPoint, 'die',  [])
            else:
                self.death_time = self.death_time_value
                self.REMOVE = True
                self.create_corpse()
    
    def create_corpse(self):
        name = 'corpse_%s_%s' % (self.name, self.death_counter)
        corpse = self.corpse(name, self.position)
        game.new_object(corpse)
    
    def die(self):
        self.alive = False
        self.death_counter+=1
        self.abort_moving()
    
    
        


class Fragile:
    "класс для объекто разбивающихся при столкновении с тайлами"
    def tile_collission(self, tile):
        self.alive = False
    
class Mortal:
    "класс для объектов убивающих живых при соприкосновении"
    def __init__(self, damage=1, alive_after_collission = False):
        self.damage = damage
        self.alive_after_collission = alive_after_collission
    
    @wrappers.player_filter(Deadly)
    def collission(self, player):
        if player.fraction!=self.fraction:
            shot = player.hit(self.damage)
            self.alive = self.alive_after_collission
            #
            if isinstance(player, Guided):
                
                if shot:
                    game.players[self.striker].plus_kills()

####################################################################

class Respawnable:
    "класс перерождающихся объектов"
    respawned = False
    def __init__(self, delay, distance):
        self.respawn_delay = delay
        self.respawn_distance = distance
        
    def remove(self):
        new_position = game.choice_position(self, 10 ,self.position)
        vector = new_position - self.position
        self.position = new_position
        self.add_event(self.prev_position, NullPoint, 'remove')
        self.add_event(self.position, NullPoint, 'move', [NullPoint.get()])
        self.respawn_message = 'Respawn', self.position
        self.alive = True
        self.respawned = True
        self.spawn()
        return False

    
    def handle_response(self):
        self.respawned = False
        return [self.respawn_message]

class DiplomacySubject:
    def __init__(self, fraction):
        self.fraction = fraction

####################################################################
class Temporary:
    "класс объекта с ограниченным сроком существования"
    def __init__(self, lifetime):
        self.lifetime = lifetime
    
    def update(self):
        self.lifetime-=1
        if self.lifetime<=0:
            self.REMOVE = True

class Striker:
    def __init__(self, strike_speed, shell, damage):
        self.strike_shell = shell
        self.strike_counter = 0
        self.strike_speed = strike_speed
        self.damage = damage
    
    @wrappers.alive_only()
    def strike_ball(self, vector):
        if self.strike_counter==0:
            ball_name = 'ball%s' % game.ball_counter
            game.ball_counter+=1
            ball = self.strike_shell(ball_name, self.position, vector, self.fraction, self.name, self.damage)
            game.new_object(ball)
            self.strike_counter+=self.strike_speed
    
    def plus_damage(self, damage):
        self.damage+=damage
            
    def update(self):
        if self.strike_counter>0:
            self.strike_counter -=1
    
    def complete_round(self):
        self.striked = False

from random import choice


