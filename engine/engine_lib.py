#!/usr/bin/env python
# -*- coding: utf-8 -*-
from share.mathlib import *
from mathlib import *

from random import choice

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
    
    @staticmethod
    def action(method):
        method.wrappers_action = True
        return method
    
    


#####################################################################
class GameObject(object):
    def __init__(self, name, position):
        self.name = name
        self._position = position
        self._location = position/LOCATIONSIZE
        self.prev_position = position
        self.REMOVE = False            
        self.alive = True
    
    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, position):
        self.prev_position = self._position
        self._position  = position
        self._location = position/LOCATIONSIZE
        game.move_object(self)
    
    
    def update(self):
        pass
    
    def collission(self, player):
        pass
        
    def tile_collission(self, tile):
        pass
    
    def add_event(self, *args):
        game.add_event(self.name, *args)
    
    
    def remove(self):
        self.add_event(self.position, NullPoint, 'remove', [])
        return True
    
    def handle_response(self):
        return []

#####################################################################
class StaticObject(GameObject):
    def __init__(self, name, position):
        GameObject.__init__(self, name, position)
    
    def update(self):
        pass

    
    def complete_round(self):
        pass




class Guided():
    "управляемый игроком объекта"
    def handle_action(self, action_name, args):
        if hasattr(self, action_name):
            method = getattr(self, action_name)
            if hasattr(method, 'wrappers_action'):
                
                return method(*args)
            else:
                print dir(method)
                print "%s isn't guided action" % action_name
                ActionError('no action %s' % action_name)
        else:
            print 'no action %s' % action_name
            raise ActionError('no action %s' % action_name)

class Solid():
    def __init__(self, radius):
        self.radius = radius
    
    def collission(self, player):
        pass

#####################################################################


        
    

####################################################################


        
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
            prev_state = player.alive
            player.hit(self.damage)
            self.alive = self.alive_after_collission
            #
            if self.striker in game.players:
                striker = game.players[self.striker]
                if isinstance(striker, Guided):
                    if prev_state and not player.alive:
                        striker.plus_kills()

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
        self.respawn_message = 'Respawn', [self.position]
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



from game import game
