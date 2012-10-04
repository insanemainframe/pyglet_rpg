#!/usr/bin/env python
# -*- coding: utf-8 -*-
from share.mathlib import *
from mathlib import *

from random import choice
from time import time



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
    def __init__(self, name):
        self.name = name
        self.REMOVE = False            
        self.alive = True
        self.delayed = False
        
    
    
    def get_location(self):
        return game.get_location(self.position)
    
    def update(self):
        pass
    
    def collission(self, player):
        pass
        
    def tile_collission(self, tile):
        pass
    
    def remove(self):
        return True
    
    

class DynamicObject(GameObject):
    def __init__(self, name, position):
        GameObject.__init__(self, name)
        
        self._position = position
        self._location = position/LOCATIONSIZE
        self._prev_position = position
        
        self.cord_changed = False
        self.position_changed = False
        game.new_object(self)
    
    @property
    def prev_position(self):
        return self._prev_position
    
    @prev_position.setter
    def prev_position(self):
        raise Warning('@prev_position.setter')
        
    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, position):
        cur_cord = position/TILESIZE
        
        if 0<=cur_cord.x<=game.world.size and 0<=cur_cord.y<=game.world.size:
            prev_cord = self._position/TILESIZE
            
            if cur_cord!=prev_cord:
                self.cord_changed = True
                
            if position!=self._position:
                self.position_changed = True
                
            prev_loc = game.get_loc_cord(self._position)
            cur_loc = game.get_loc_cord(position)
            if prev_loc!=cur_loc:
                game.change_location(self.name, prev_loc, cur_loc)
            
            self._prev_position = self._position
            self._position  = position
        else:
            print 'Invalid position %s %s' % (position, self.name)
    
    def add_event(self, action, args, timeout=0):
        object_type = self.__class__.__name__
        vector = self.position-self.prev_position
        game.add_event(self.name, object_type, self.position, vector, action, args, timeout, self.delayed)
    
    def complete_round(self):
        self.cord_changed = False
        self.position_changed = False

class StaticObject(GameObject):
    name_counter =0 
    def __init__(self, position):
        counter = StaticObject.name_counter
        StaticObject.name_counter+=1
    
        name = '%s_%s' % (self.__class__.__name__, counter)
        
        GameObject.__init__(self, name)
        
        self.position = position
        
        game.new_static_object(self)
    
    def get_tuple(self):
        return self.__class__.__name__, self.position
    
    def add_event(self, action, args, timeout=0):
        object_type = self.__class__.__name__
        game.add_static_event(self.name, object_type, self.position, action, args, timeout, delayed)

    
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
        self.hitted = 0
    
    def spawn(self):
        self.alive = True
        self.hp = self.hp_value
        
    

    
    def hit(self, hp):
        self.hitted = 10
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
            if self.hitted:
                self.add_event('defend', ())
                self.hitted-=1
            else:
                if self.hp<self.hp_value:
                    self.hp+=self.heal_speed
        else:
            if self.death_time>0:
                self.death_time-=1
                self.add_event('die',  ())
            else:
                self.death_time = self.death_time_value
                self.REMOVE = True
                self.create_corpse()
    
    def create_corpse(self):
        name = 'corpse_%s_%s' % (self.name, self.death_counter)
        corpse = self.corpse(name, self.position)
        game.new_static_object(corpse)
    
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
        self.add_event('remove',())
        self.add_event('move', (NullPoint.get(),))
        self.respawn_message = 'Respawn', [self.position]
        self.alive = True
        self.respawned = True
        self.spawn()
        return False

    
    def handle_response(self):
        self.respawned = False
        return self.respawn_message

class DiplomacySubject:
    def __init__(self, fraction):
        self.fraction = fraction
        self.invisible = 0
    
    def set_invisible(self, invisible_time):
        self.invisible = invisible_time
    
    def update(self):
        if self.invisible:
            self.invisible-=1

####################################################################
class Temporary:
    "класс объекта с ограниченным сроком существования"
    def __init__(self, lifetime):
        self.lifetime = lifetime
        self.creation_time = time()
    
    def update(self):
        t = time()
        if t-self.creation_time >= self.lifetime:
            self.REMOVE = True



from game import game
