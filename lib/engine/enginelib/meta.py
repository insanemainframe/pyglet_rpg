#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from share.errors import *

from share.point import Point

from engine.tuples import ObjectTuple, OnlineTuple, Event
from engine.mathlib import *

from random import random
from time import time
from weakref import proxy, ProxyType




class GameObject(object):
    BLOCKTILES = []
    SLOWTILES = {}
    __name_counter = 0
    def __init__(self, name = None):
        if not name:
            GameObject.__name_counter += 1
            object_type = self.__class__.__name__
            n = GameObject.__name_counter
            self.name = "%s_%s" % (object_type, n)
             
        else:
            assert isinstance(name, str)
            self.name = name

        self.alive = True
        
        self.gid = str(hash((name, random())))

        self.cord_changed = True
        self.position_changed = True
        self.location_changed = False
        self._REMOVE = False
        self._owner = None


    
    def handle_creating(self):
        pass

        
    
    def handle_remove(self):
        return True

    def handle_new_world(self):
        pass
    
    def regid(self):
        self.gid = str(hash((self.name, self.position, random())))
        
    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, position):
        raise AttributeError('@position.setter')


    @property
    def prev_position(self):
        return self._prev_position
    
    @prev_position.setter
    def prev_position(self):
        raise AttributeError('@prev_position.setter')


    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, owner):
        assert owner is None or isinstance(owner, ProxyType)
        self._owner = owner
    
    def set_position(self, position):
        "принудительная установка позиции"
        assert isinstance(position, Point)

        self._position = position
        self._prev_position = position

        self.cord = position/TILESIZE
        self.prev_cord = self.cord
        
        #self.location.update_tiles(self, prev_cord, self.cord)
        self.chunk.set_new_players()

            
    def change_position(self, new_position):
        "вызывается при смене позиции"
        if not new_position==self._position:
            self.chunk.change_position(proxy(self), new_position)

    
    
    
    def verify_chunk(cls, location, chunk):
        return True
    
    @classmethod
    def verify_position(cls, location, chunk, i ,j):
        is_free = not location.get_voxel(i, j)
        non_block = not location.map[i][j] in cls.BLOCKTILES
        return is_free and non_block
    
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

        return ObjectTuple(self.gid, self.name, object_type, self.prev_position, self.get_args())

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
    def is_active(self):
        return True
    
class Updatable(object):
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
        

    def _end_round(self):
        self.cord_changed = False
        self.position_changed = False
        self.has_events = False
        self.__events__.clear()

    def complete_round(self):
        pass



class HierarchySubject:
    def __init__(self):
        self._master = None
        self._slaves = {}

    @property
    def master(self):
        return self._master

    @master.setter
    def master(self, new_master):
        assert new_master is None or isinstance(new_master, ProxyType)
        self._master = new_master

    def bind_slave(self, slave):
        assert isinstance(slave, ProxyType)

        self._slaves[slave.name] = slave
        slave.master = proxy(self)
        slave.handle_bind_master()
    
    def unbind_slave(self, slave):
        self._slaves[slave.name].master = None
        del self._slaves[slave.name]
        slave.handle_unbind_master()

    def unbind_all_slaves(self):
        slaves = self._slaves.values()
        for slave in slaves:
            self.unbind_slave(slave)

    def get_slaves(self):
        return self._slaves.values()

    def handle_unbind_master(self):
        pass

    def handle_bind_master(self):
        pass






class Container:
    def __init__(self):
        self._related_objects = {}

    def bind(self, related):
        location = related.location
        location.pop_object(related)

        self._related_objects[related.name] = related
        related.owner = proxy(self)

        self.handle_bind(related)

    def pop_related(self, name):
        return self._related_objects.pop(name)

    
    def unbind(self, related):
        related.owner = None
        self.location.new_object(related, position = self.position)
        del self._related_objects[related.name]

    def unbind_all(self):
        relateds = self._related_objects.values()
        for related in relateds:
            self.unbind(related)


    def handle_bind(self, related):
        pass


    



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
    

    def get_online_tuple(self, cname):
        if self.name!=cname:
            name = "(%s)" % self.name
        else:
            name = self.name

        return OnlineTuple(name, self.kills)
    


class Solid(object):
    def __init__(self, radius):
        self.radius = radius
    
    def collission(self, player):
        pass

class Impassable(Solid):
    pass




        
class Breakable(object):
    "класс для живых объектов"
    heal_time = 1200
    def __init__(self, hp, corpse_type = None):
        self.hp_value = hp
        self.heal_speed = self.hp_value/float(self.heal_time)
        self.death_time = death_time
        self.death_time_value = death_time
        self.corpse_type = corpse_type
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
        if self.corpse_type:
            corpse = self.corpse_type()
            self.location.new_object(corpse)
    
    def die(self):
        self.alive = False
        self.death_counter+=1
        self.abort_moving()
    
    def get_args(self):
        return {'hp': self.hp, 'hp_value':self.hp_value}

    def handle_respawn(self):
        self.spawn()
    
    
        


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
        if isinstance(player, Breakable):
            if player.fraction!=self.fraction:
                prev_state = player.alive
                player.hit(self.damage)
                if not self.alive_after_collission:
                    self.add_to_remove()
                #
                try:
                    if isinstance(self.striker, Guided):
                        if prev_state and not player.alive:
                            self.striker.plus_kills()
                except:
                    pass

####################################################################

class Respawnable(object):
    "класс перерождающихся объектов"
    respawned = False
    def __init__(self, delay, distance):
        self.respawn_delay = delay
        self.respawn_distance = distance
        
    def remove(self):
        return False
    
    def handle_remove(self):
        return False




class DiplomacySubject(object):
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
    def __init__(self):
        GameObject.__init__(self)
        Temporary.__init__(self, 5)
    
    def update(self):
        GameObject.update(self)
        Temporary.update(self)


class Savable(object):
    def __save__(self):
        return ()

    @staticmethod
    def __load__():
        return ()