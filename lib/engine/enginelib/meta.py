#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from share.errors import *

from engine.mathlib import Cord, Position, ChunkCord

from engine.tuples import ObjectTuple, OnlineTuple, Event
from engine.mathlib import *

from random import random
from time import time
from weakref import proxy, ProxyType
from collections import defaultdict




class GameObject(object):
    BLOCKTILES = []
    SLOWTILES = {}
    __name_counter = 0
    cord_binded = False

    def __init__(self, name = None):
        if not name:
            GameObject.__name_counter += 1
            object_type = self.__class__.__name__
            n = GameObject.__name_counter
            self.name = "%s_%s" % (object_type, n)
             
        else:
            assert isinstance(name, str)
            self.name = name

        
        self.gid = str(hash((name, random())))

        
        self.__REMOVE = False
        self._owner = None

        self._position = None

    def is_alive(self):
        return not self.__REMOVE




    def add_event(self, *args, **kwargs):
        pass






    
    def handle_creating(self):
        pass

    
    
    def handle_remove(self):

        return True

    def handle_new_location(self):
        pass
    
    def regid(self):
        self.gid = str(hash((self.name, time(), random())))
        
    @property
    def position(self):
        return self._position
    
    @property
    def prev_position(self):
        return self._prev_position





    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, owner):
        assert owner is None or isinstance(owner, ProxyType)
        self._owner = owner
    
    def set_position(self, position):
        "принудительная установка позиции"
        assert isinstance(position, Position)

        self._prev_position = position

        self._position = position
        # self._prev_position = position

        self.cord = position.to_cord()
        # self.prev_cord = self.cord
        
        #self.location.update_tiles(self, prev_cord, self.cord)
        self.chunk.set_new_players()

            
    

    
    
    
    def verify_chunk(self, location, chunk):
        return True
    
    def verify_position(self, location, chunk, cord, generation = True):
        # print self.name, 'BLOCKTILES', location.get_tile(cord), self.BLOCKTILES
        blocked = location.get_tile(cord) in self.BLOCKTILES
        if blocked:
            print 'blocked', self.name, self.BLOCKTILES
            return False
        else:
            return True

      
    
    

    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, player):
        return self.name==player.name
    
    def __ne__(self, player):
        return self.name!=player.name
    

    


    def add_to_remove(self):
        self.chunk.add_to_remove(self.name)

    def add_delay(self, action, *args):
        self.chunk.delay_args[self.gid] = (action, args)

    def get_tuple(self, name):
        if name==self.name:
            object_type = 'Self'
        else:
            object_type = self.__class__.__name__

        return ObjectTuple(self.gid, self.name, object_type, self.prev_position, self.get_args())

    def get_args(self):
        return {}



    def __str__(self):
        return self.name




class ActiveState(object):
    "метка"
    def is_active(self):
        return True

class Updatable(object):
    def mixin(self):
        pass



class HierarchySubject(object):
    def mixin(self):
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

    def handle_remove(self):
        self.master.unbind_slave(self)


    def __del__(self):
        del self._master
        del self._slaves






class Container(object):
    def mixin(self):
        self.__related_objects = defaultdict(dict)

    def bind(self, related):
        location = related.location
        location.pop_object(related)

        self.add_related(related)

        self.handle_bind(related)

    def pop_related(self, related_type):
        if related_type in self.__related_objects:
            slot = self.__related_objects[related_type]
            if slot:
                name, related = slot.popitem()
                if not slot:
                    del self.__related_objects[related_type]
                return related

    def add_related(self, related):
        related_type = related.__class__.__name__

        slot = self.__related_objects[related_type]
        slot[related.name] = related

        related.owner = proxy(self)

    
    def unbind(self, related):
        related_type = related.__class__.__name__
        slot = self.__related_objects[related_type]
        name = related.name
        assert name in slot

        related = slot.popitem(name)
        related.owner = None

        self.location.new_object(related, position = self.position)
        self.handle_unbind(related)

    def unbind_all(self):
        for slot in self.__related_objects.values():
            for related in slot.values():
                self.location.new_object(related, position = self.position)
            slot.clear()

        self.__related_objects.clear()

    def get_related_dict(self):
        return {r_type:len(slot) for r_type, slot in  self.__related_objects.items()}



    def handle_bind(self, related):
        pass

    def __del__(self):
        del self.__related_objects


    



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

    def handle_quit(self):
        pass

    def is_guided_changed(self):
        return self.location.is_guided_changed()

    def get_online_list(self):
        return self.location.get_guided_list(self.name)
    


class Solid(object):
    def mixin(self, radius):
        self.radius = radius
    
    def collission(self, player):
        pass

    def tile_collission(self, tile):
        pass

class Impassable(Solid):
    pass




        
class Breakable:
    "класс для живых объектов"
    __heal_time = 120

    def mixin(self, hp = 10):
        self.__hp_value = hp
        self.__HP = hp

        self.heal_speed = self.__hp_value/float(self.__heal_time)
        self.__corpse_type = None
        self.death_counter = 0
        self.hitted = 0

        self.prev_heal = time()

    def set_hp(self, hp_value):
        self.__hp_value = hp_value
        self.__HP = hp_value

    def get_hp(self):
        return self.__HP

    def get_hp_value(self):
        return self.__hp_value

    def set_corpse(self, corpse_type):
        self.__corpse_type = corpse_type


    @property
    def __hp(self):
        return self.__HP

    @__hp.setter
    def __hp(self, new_hp):
        if new_hp!=self.__hp:
            if new_hp>self.__hp_value:
                new_hp = self.__hp_value
            elif new_hp<0:
                new_hp = 0
            self.__HP = new_hp

        self.add_event('change_hp', self.__hp_value, self.__HP)

    @property
    def hp_value(self):
        return self.__hp_value

    @hp_value.setter
    def hp_value(self, new_hp_value):
        if new_hp_value>0:
            self.__hp_value = new_hp_value
            self.add_event('change_hp', self.__hp_value, self.__HP)
            self.add_event('defend')
    
        
    
    def hit(self, hp):
        self.__hp = self.__hp-hp
        
        
        if self.__hp<=0:
            self.add_to_remove()
            self.__hp = self.__hp_value
            return True
        else:
            return False
    
    def heal(self, hp = False):
        if not hp:
            hp = self.heal_speed

        self.__hp += hp


    
    def plus_hp(self, armor):
        self.__hp_value+=armor
        self.heal_speed = self.__hp_value/float(self.heal_time)
    
    def update(self):
        cur_time = time()
        delta = cur_time - self.prev_heal

        heal_hp = self.heal_speed * delta
        self.heal(heal_hp)

        self.prev_heal = cur_time

    
    def create_corpse(self):
        if self.__corpse_type:
            corpse = self.__corpse_type()
            self.location.new_object(corpse, position = self.position)
    
    
    def get_args(self):
        return {'hp': self.__hp, 'hp_value':self.__hp_value}


    def handle_remove(self):
        self.add_delay('die')
        self.create_corpse()



    def handle_respawn(self):
        self.__hp = self.__hp_value

    
    
        


class Fragile(object):
    "класс для объекто разбивающихся при столкновении с тайлами"
    def tile_collission(self, tile):
        self.add_to_remove()
        
    
class Mortal(object):
    "класс для объектов убивающих живых при соприкосновении"
    def mixin(self, damage=1, alive_after_collission = False):
        self.damage = damage
        self.alive_after_collission = alive_after_collission
    
    def collission(self, player):
        if isinstance(player, Breakable):
            if player.name!=self.name:
                is_dead = player.hit(self.damage)
                if not self.alive_after_collission:
                    self.add_to_remove()
                #
                try:
                    if isinstance(self.striker, Guided) and is_dead:
                            self.striker.plus_kills()
                except:
                    pass

####################################################################

class Respawnable(object):
    "класс перерождающихся объектов"
    respawned = False
    def mixin(self, delay, distance):
        pass
        
    def remove(self):
        return False
    
    def handle_remove(self):
        return False




class DiplomacySubject(object):
    fraction = 'neutral'
    def mixin(self, fraction = 'neutral'):
        self.fraction = fraction
        self.invisible = 0
    
    def set_fraction(self, fraction):
        self.fraction = fraction

    def set_invisible(self, invisible_time):
        self.invisible = invisible_time
    
    def update(self):
        if self.invisible:
            self.invisible-=1

####################################################################
class Temporary(Updatable):
    "класс объекта с ограниченным сроком существования"
    def mixin(self, lifetime):
        Updatable.mixin(self)
        self.__lifetime = lifetime
        self.__creation_time = time()
    
    def update(self, ):
        cur_time = time()

        if cur_time - self.__creation_time > self.__lifetime:
            print 'remove'
            self.add_to_remove()



class Groupable:
    group_chance = 98

    def verify_position(self, location, chunk, cord, generation = True):
        if not GameObject.verify_position(self, location, chunk, cord, generation = True):
            return False
        self_type = self.__class__

        if generation:
            if not hasattr(self_type, 'gen_counter'):
                self_type.gen_counter = 0

            if self_type.gen_counter<50:
                self_type.gen_counter+=1
                return True
            else:
                for player in sum(location.get_near_voxels(cord), []):
                    if isinstance(player, self_type):
                        return True
                if chance(self.group_chance):
                    return False
                else:
                    return True
        else:
            return True



class Savable(object):
    def __save__(self):
        return ()

    @classmethod
    def __load__(cls, location):
        return cls()

class SavableRandom(Savable):
    pass


class OverLand:
    BLOCKTILES = ['water', 'ocean', 'lava', 'stone']

class OverWater:
    BLOCKTILES = ['grass', 'forest', 'bush', 'stone', 'underground', 'lava']