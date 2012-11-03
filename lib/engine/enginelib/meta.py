#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from engine.errors import *

from share.point import Point
from engine.mathlib import *
from engine.enginelib import wrappers
from engine.events import Event

from random import choice, random
from time import time
from weakref import proxy, ProxyType


class GameObject(object):
    BLOCKTILES = []
    SLOWTILES = {}
    __name_counter = 0
    def __init__(self, position, name = None):
        assert isinstance(position, Point)

        if not name:
            GameObject.__name_counter += 1
            object_type = self.__class__.__name__
            n = GameObject.__name_counter
            self.name = "%s_%s" % (object_type, n)
             
        else:
            assert isinstance(name, str)
            self.name = name

        self.alive = True
        
        
        self._position = position
        self.cord = position/TILESIZE
        self._prev_position = position
        
        self.gid = str(hash((name, position, random())))
        
        

        self.cord_changed = True
        self.position_changed = True
        self.location_changed = False
        self._REMOVE = False
    
    def handle_creating(self):
        pass
    
    def handle_remove(self):
        return True
    
    def regid(self):
        self.gid = str(hash((self.name, self.position, random())))
        
    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, position):
        raise Exception('Denied')


    @property
    def prev_position(self):
        return self._prev_position
    
    @prev_position.setter
    def prev_position(self):
        raise Exception('@prev_position.setter')

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, owner):
        self._owner = proxy(owner)
    
    def set_position(self, position):
        "принудительная установка позиции"
        size = self.location.size*TILESIZE
        if 0<=position.x<=size and 0<=position.y<=size:
            prev_cord = self._position/TILESIZE
            self._position = position
            self._prev_position = position
            self.cord = position/TILESIZE
            
            self.location.update_tiles(self, prev_cord, self.cord)
            self.chunk.set_new_players()
            
        else:
            data = (position, self.name, self.location.name, self.location.size)
            self.location.handle_over_range(self, position)
            raise Warning('Invalid position %s %s location %s size %s' % data)
            
    def change_position(self,position):
        "вызывается при смене позиции"
        if not position==self._position:
            
            cur_cord = position/TILESIZE
            prev_cord = self._position/TILESIZE
            
            if 0<=cur_cord.x<=self.location.size and 0<=cur_cord.y<=self.location.size:
                prev_cord = self._position/TILESIZE
                
                if cur_cord!=prev_cord:
                    self.cord_changed = True
                    self.cord = cur_cord
                    
                if position!=self._position:
                    self.position_changed = True
                    
                prev_loc = self.chunk.cord
                cur_loc = self.location.get_loc_cord(position)
                if prev_loc!=cur_loc:
                    self.location.change_chunk(self, prev_loc, cur_loc)
                
                self._prev_position = self._position
                self._position  = position
                self.chunk.set_new_players()
                #
                self.location.update_tiles(self, prev_cord, cur_cord)
                
            else:
                data = (position, self.name, self.location.name, self.location.size)
                self.location.handle_over_range(self, position)
                self.flush()

    
    
    
    def choice_chunk(cls, location, chunk):
        return True
    
    
    def choice_position(location_map, chunk, i ,j):
        return True
    
    def handle_change_location(self):
        pass

    def handle_respawn(self):
        pass

    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, player):
        return self.name==player.name
    
    def __ne__(self, player):
        return self.name!=player.name
    
    def update(self):
        pass
    
    def collission(self, player):
        pass
        
    def tile_collission(self, tile):
        pass
    


    def add_to_remove(self):
        self._REMOVE = True

    def get_tuple(self, name):
        if name==self.name:
            object_type = 'Self'
        else:
            object_type = self.__class__.__name__
        return self.gid, self.name, object_type, self.prev_position, self.get_args()

    def get_args(self):
        return {}

    

    def __del__(self):
        try:
            if not self.location.game.stopped:
                print ('del %s' % self.name)
        except:
            pass

    def __str__(self):
        return self.name


class ActiveState:
    "метка"
    pass  
    
class Updatable:
    def __init__(self):
        self.__events__ = set()
        self.has_events = False

    def add_event(self, action, *args, **kwargs):
        if 'timeout' in kwargs:
            timeout = kwargs['timeout']
        else:
            timeout = 0
        self.__events__.add(Event(action, args, timeout))
        self.chunk.set_event()
        self.has_events = True

    def get_events(self):
        return self.__events__

    def clear_events(self):
        self.__events__.clear()

    def complete_round(self):
        self.cord_changed = False
        self.position_changed = False
        self.has_events = False



class HierarchySubject:
    def __init__(self):
        self._master = None
        self.slaves = {}

    @property
    def master(self):
        return self._master

    @master.setter
    def master(self, new_master):
        assert isinstance(new_master, ProxyType)
        self._master = new_master

    def bind_slave(self, slave):
        assert isinstance(slave, ProxyType)
        self.slaves[slave.name] = slave
    
    def unbind_slave(self, slave):
        del self.slaves[slave.name]

    def get_slaves(self):
        return self.slaves.values()

    def bind_master(self, master):
        self.master = master
        self.master.bind_slave(proxy(self))
        self.handle_bind_master()

    def unbind_master(self):
        self.master.unbind_slave(self)
        self.master = None


class Container:
    def __init__(self):
        self._owner = None
        self.related_objects = set()

    def bind(self, related):
        self.related_objects.add(related)
        related.owner = self
        related.location = self.location
        related.chunk = self.chunk
    
    def unbind(self, related):
        self.related_objects.remove(related)
        related.owner = None


    



class Guided(ActiveState):
    "управляемый игроком объекта"
    __actions__ = {}
    
    def handle_action(self, action_name, args):
        if action_name in self.__actions__:
            method = self.__actions__[action_name]
            return method(*args)

        else:
            print('no action %s' % action_name)
            raise ActionError('no action %s' % action_name)
    

    
    @staticmethod
    def action(method):
        method.wrappers_action = True
        return method
    


class Solid():
    def __init__(self, radius):
        self.radius = radius
    
    def collission(self, player):
        pass

class Impassable(Solid):
    pass




        
class Deadly:
    "класс для живых объектов"
    heal_time = 1200
    def __init__(self, corpse, hp, death_time=20):
        self.hp_value = hp
        self.heal_speed = self.hp_value/float(self.heal_time)
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
            
            self.add_event('change_hp', self.hp_value, self.hp if self.hp>0 else 0)
            if self.hp<=0:
                self.die()
                self.hp = self.hp_value
                return True
            else:
                return False
        else:
            return False
    
    def heal(self, hp = False):
        if not hp:
            hp = self.heal_speed

        new_hp = self.hp+ hp
        if new_hp>self.hp_value:
            new_hp = self.hp_value
        
        self.hp = new_hp
        self.add_event('change_hp', self.hp_value, self.hp)
    
    def plus_hp(self, armor):
        self.hp_value+=armor
        self.heal_speed = self.hp_value/float(self.heal_time)
        self.add_event('change_hp', self.hp_value, self.hp)
    
    def update(self):
        if self.alive:
            if self.hitted:
                self.add_event('defend')
                self.hitted-=1
            else:
                if self.hp<self.hp_value:
                    self.heal()
        else:
            if self.death_time>0:
                self.death_time-=1
                self.add_event('die')
            else:
                self.death_time = self.death_time_value
                self.add_to_remove()
                self.create_corpse()
    
    def create_corpse(self):
        name = 'corpse_%s_%s' % (self.name, self.death_counter)
        corpse = self.corpse(name, self.position)
        self.location.new_object(corpse)
    
    def die(self):
        self.alive = False
        self.death_counter+=1
        self.abort_moving()
    
    def get_args(self):
        return {'hp': self.hp, 'hp_value':self.hp_value}
    
    
        


class Fragile:
    "класс для объекто разбивающихся при столкновении с тайлами"
    def tile_collission(self, tile):
        self.alive = False
    
class Mortal:
    "класс для объектов убивающих живых при соприкосновении"
    def __init__(self, damage=1, alive_after_collission = False):
        self.damage = damage
        self.alive_after_collission = alive_after_collission
    
    def collission(self, player):
        if isinstance(player, Deadly):
            if player.fraction!=self.fraction:
                prev_state = player.alive
                player.hit(self.damage)
                if not self.alive_after_collission:
                    self.add_to_remove()
                #
                if self.striker in self.location.game.players:
                    striker = self.location.game.players[self.striker]
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
        return False
    
    def handle_remove(self):
        cord = self.location.size*TILESIZE/2
        start = Point(cord, cord)
        new_position = self.location.choice_position(self, self.location.main_chunk)
        
        self.set_position(new_position)
        
        self.alive = True
        self.flush()
        self.regid()
        self.respawned = True
        self.spawn()
        self.handle_respawn()
        return False



class DiplomacySubject:
    fraction = 'neutral'
    def __init__(self, fraction):
        self.fraction = fraction
        self.invisible = 0
    
    def set_invisible(self, invisible_time):
        self.invisible = invisible_time
    
    def update(self):
        if self.invisible:
            self.invisible-=1

####################################################################
class Temporary(Updatable):
    "класс объекта с ограниченным сроком существования"
    def __init__(self, lifetime):
        Updatable.__init__(self)
        self.lifetime = lifetime
        self.creation_time = time()
    
    def update(self):
        t = time()
        if t-self.creation_time >= self.lifetime:
            self.add_to_remove()




class Corpse(GameObject, Temporary):
    "кости остающиеся после смерти живых игроков"
    def __init__(self, name, position):
        GameObject.__init__(self, position)
        Temporary.__init__(self, 5)
    
    def update(self):
        GameObject.update(self)
        Temporary.update(self)


class Savable:
    def __save__(self):
        return [self.position.get()]

    @staticmethod
    def __load__((x,y)):
        return [Point(x,y)]