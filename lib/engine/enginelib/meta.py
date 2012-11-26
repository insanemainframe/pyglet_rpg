#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from server_logger import debug
from engine.errors import *

from engine.mathlib import Cord, Position, ChunkCord

from engine.tuples import ObjectTuple, OnlineTuple, Event
from engine.mathlib import *

from random import random
from time import time
from weakref import proxy, ProxyType
from collections import defaultdict


class BaseObject(object):
    BLOCKTILES = []
    SLOWTILES = {}
    __name_counter = 0
    cord_binded = False

    def __init__(self, name = None):
        if not name:
            BaseObject.__name_counter += 1
            object_type = self.__class__.__name__
            n = BaseObject.__name_counter
            self.name = "%s_%s" % (object_type, n)
             
        else:
            assert isinstance(name, str)
            self.name = name

        self.gid = str(hash((name, random())))
        self.__REMOVE = False
        self.__created = False
        self.__activity = 0

        self.cord_changed = True
        self.position_changed = True
        self.location_changed = False

    def __run(self):
        self.__created = True
        if self.__activity>0:
            self.chunk.add_to_update(self.name)
        

    def add_activity(self, Class=None):
        # debug  'add to update', self
        self.__activity += 1
        if self.__activity == 1 and self.__created:
            self.chunk.add_to_update(self.name)

        assert self.__activity > 0

    def pop_activity(self):
        # debug  'pop_activity', self, Class
        if self.__activity > 0:
            self.__activity -= 1
            if self.__activity == 0:
                self.chunk.pop_from_update(self.name)

        assert self.__activity >= 0

    def get_activity(self):
        return bool(self.__activity)


    def add_event(self, action, *args):
        self.chunk.add_event(self.gid, Event(action, args))

    def is_alive(self):
        return not self.__REMOVE

    def regid(self):
        self.gid = str(hash((self.name, time(), random())))
        

    @property
    def position(self):
        return self._position
    
    @property
    def prev_position(self):
        return self._prev_position
    
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

    def change_position(self, new_position):
        "вызывается при смене позиции"
        assert isinstance(new_position, Position)
        
        if not new_position == self._position:

            self.chunk.change_position(proxy(self), new_position)

    def update_position(self, move_vector):
        assert isinstance(move_vector, Position)

        if move_vector:
            self.change_position(self.position + move_vector)

            self.add_event('move',  move_vector.get())
    

    def __complete_round__(self):
        self.cord_changed = False
        self.position_changed = False
        self.location_changed = False


    def add_to_remove(self, reason = None):
        self.__REMOVE = True
        if isinstance(self, Guided):
            debug('add_to_remove', reason)
        
        self.chunk.add_to_remove(self.name)

    def add_delay(self, action, *args):
        self.chunk.add_delay(self.gid, action, args)

    def get_tuple(self, name):
        if name == self.name:
            object_type = 'Self'
        else:
            object_type = self.__class__.__name__

        return ObjectTuple(self.gid, self.name, object_type, self.prev_position, self.get_args())

    def get_args(self):
        return {}


    def verify_chunk(self, location, chunk):
        return True
    
    def verify_position(self, location, chunk, cord, generation=True):
        # debug self.name, 'BLOCKTILES', location.get_tile(cord), self.BLOCKTILES
        blocked = location.get_tile(cord) in self.BLOCKTILES
        if blocked:
            #debug( 'blocked', self.name, self.BLOCKTILES)
            return False
        else:
            return True


    def handle_creating(self):
        pass

    def handle_remove(self):
        return True

    def __str__(self):
        return "<%s> % s" % (self.__class__.__name__, self.name)

    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, player):
        return self.name == player.name
    
    def __ne__(self, player):
        return self.name != player.name


class BaseObjectFactory(object):
    pass


class ActiveState(object):
    "метка"
    def is_active(self):
        return True


class HierarchySubject(object):
    def mixin(self):
        self.__master = None
        self.__slaves = {}


    def get_master(self):
        return self.__master

    def has_master(self):
        return bool(self.__master)

    def bind_slave(self, slave):
        assert isinstance(slave, ProxyType)
        assert isinstance(slave, HierarchySubject)
        assert slave.name not in self.__slaves

        self.__slaves[slave.name] = slave
        slave.__master = proxy(self)
        slave.handle_bind_master(proxy(self))
    
    def unbind_slave(self, slave):
        assert slave.name in self.__slaves

        self.__slaves[slave.name].__master = None
        del self.__slaves[slave.name]
        slave.handle_unbind_master()

    def unbind_all_slaves(self):
        slaves = self.__slaves.values()
        for slave in slaves:
            self.unbind_slave(slave)

    def get_slaves(self):
        return self.__slaves.values()

    def handle_unbind_master(self):
        pass

    def handle_bind_master(self, master):
        pass

    def handle_remove(self):
        if self.__master:
            self.__master.unbind_slave(self)


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

        related._Containerable__owner = proxy(self)

    
    def unbind(self, related):
        related_type = related.__class__.__name__
        slot = self.__related_objects[related_type]
        name = related.name
        assert name in slot

        related = slot.popitem(name)
        del related._Containerable__owner

        self.location.new_object(related, position = self.position)
        self.handle_unbind(related)

    def unbind_all(self):
        for slot in self.__related_objects.values():
            for related in slot.values():
                self.location.new_object(related, position = self.position)
            slot.clear()

        self.__related_objects.clear()

    def get_related_dict(self):
        return {r_type: len(slot) for r_type, slot in  self.__related_objects.items()}

    def handle_bind(self, related):
        pass


class Containerable(object):
    def get_owner(self):
        return self.__owner

    def set_owner(self, owner):
        assert isinstance(owner, Container)
        owner.bind(self)

    def collission(self, player):
        if isinstance(player, Container):
            self.set_owner(player)


class Guided(ActiveState):
    "управляемый игроком объекта"
    __actions = {}

    def set_actions(self, **action_dict):
        for name, handler in action_dict.items():
            assert isinstance(name, str)
            assert callable(handler)

            self.__actions[name] = handler
    
    def handle_action(self, action_name, args):
        if action_name in self.__actions:
            method = self.__actions[action_name]
            return method(*args)
        else:
            debug('no action %s' % action_name)
            raise ActionError('no action %s' % action_name)
    

    def get_online_tuple(self, cname):
        if self.name != cname:
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
    def mixin(self, passable=True):
        self.__passable = passable

    def is_passable(self):
        return self.__passable

    def set_passable(self, value):
        assert isinstance(value, bool)
        self.__passable = value
    
    def collission(self, player):
        pass

    def tile_collission(self, tile):
        pass

        
class Breakable(object):
    "класс для живых объектов"

    def mixin(self, hp=10, heal_time=120):
        assert isinstance(hp, int) and hp > 0
        assert isinstance(heal_time, int) and heal_time >= 0
        self.__hp = hp
        self.__hp_value = hp
        self.__heal_time = heal_time

        if self.__heal_time > 0:
            self.__heal_speed = self.__hp / float(self.__heal_time)
        else:
            self.__heal_speed = 0

        self.__corpse_type = None
        self.death_counter = 0
        self.hitted = 0

        self.__prev_time = time()


    def __add_activity(self, message=None):
        if self.__heal_speed:
            self.add_activity(message)

    def set_hp(self, new_hp):
        if new_hp > 0:
            self.__hp = new_hp
            if self.__hp_value > self.__hp:
                self.__hp_value = self.__hp

            self.__heal_speed = self.__hp / float(self.heal_time)
            self.add_event('change_hp', self.__hp, self.__hp_value)

    def update_hp(self, value):
        self.set_hp(hp_max + value)

    def get_hp(self):
        return self.__hp

    def get_hp_value(self):
        return self.__hp_value

    def set_corpse(self, corpse_type):
        self.__corpse_type = corpse_type


    def __update_hp_value(self, value):
        self.__set_hp_value(self.__hp_value + value)

    def __set_hp_value(self, value):
        if value != self.__hp_value:
            if value > self.__hp:
                value = self.__hp
            elif value < 0:
                value = 0

            if value < self.__hp_value:
                self.add_event('defend')
            self.__hp_value = value

        self.add_event('change_hp', self.__hp, self.__hp_value)


    def hit(self, hp):
        self.__add_activity('Breakable')

        self.__update_hp_value(-hp)
        
        if self.__hp_value <= 0:
            print self.name, 'died'
            self.add_to_remove('died')
            return True
        else:
            return False
    
    def heal(self, hp=False):
        if not hp:
            hp = self.__heal_speed

        self.__update_hp_value(hp)
        if self.__hp_value == self.__hp:
            self.pop_activity()
    

    def __update__(self, cur_time):
        cur_time = time()
        delta = cur_time - self.__prev_time

        heal_hp = self.__heal_speed * delta
        self.heal(heal_hp)

        self.__prev_time = cur_time

    
    def get_args(self):
        return {'hp': self.__hp_value, 'hp_value':self.__hp}

    def handle_remove(self):
        self.add_delay('die')

        if self.__corpse_type:
            corpse = self.__corpse_type()
            self.location.new_object(corpse, position=self.position)

    def handle_respawn(self):
        self.__hp_value = self.__hp


class Fragile(object):
    "класс для объекто разбивающихся при столкновении с тайлами"
    def tile_collission(self, tile):
        self.add_to_remove('Fragile')
        
    
class Mortal(object):
    "класс для объектов убивающих живых при соприкосновении"
    def mixin(self, damage=1, alive_after_collission=False):
        self.__damage = damage
        self.__alive_after = alive_after_collission
    
    def collission(self, player):
        if isinstance(player, Breakable):
            damage = (self.__damage * self.get_speed())
            is_dead = player.hit(damage)
            if not self.__alive_after:
                self.add_to_remove('Mortal')
            #
            try:
                if isinstance(self.striker, Guided) and is_dead:
                        self.striker.plus_kills()
            except:
                pass


class SmartMortal(Mortal):
    def collission(self, player):
        if not isinstance(player, DiplomacySubject) or self.is_enemy(player):
            Mortal.collission(self, player)


class Respawnable(object):
    "класс перерождающихся объектов"
    respawned = False

    def mixin(self, delay, distance):
        pass
        
    def remove(self):
        return False

    def handle_respawn(self):
        pass
    
    def handle_remove(self):
        return False


class DiplomacySubject(object):

    def mixin(self, fraction='neutral'):
        self.__fraction = fraction
        self.__spy_mode = False
    
    def set_fraction(self, fraction):
        self.__fraction = fraction

    def get_fraction(self):
        return self.__fraction

    def is_spy(self):
        return self.__spy_mode

    def set_spy_mode(self, invisible_time):
        self.__spy_mode = True
        self.__prev_time = time()
        self.__spy_mode_time = invisible_time

    def unset_spy_mode(self):
        self.__spy_mode = False
        self.__prev_time = None
        self.__spy_mode_time = None


    def is_ally(self, player):
        assert isinstance(player, DiplomacySubject)

        return player.__spy_mode or player.__fraction == self.__fraction

    def is_enemy(self, player):
        assert isinstance(player, DiplomacySubject)

        return player.__fraction != self.__fraction and player.__fraction != 'neutral' and not player.__spy_mode
    
    def __update__(self, cur_time):
        if self.__spy_mode:
            if time() - self.__prev_time > self.__spy_mode_time:
                self.unset_spy_mode()


class Temporary(object):
    "класс объекта с ограниченным сроком существования"
    
    def mixin(self, lifetime):
        self.add_activity('Temporary')
        
        self.__lifetime = lifetime
        self.__creation_time = time()
    
    def __update__(self, cur_time):
        if cur_time - self.__creation_time > self.__lifetime:
            self.add_to_remove('Temporary')


class Savable(object):
    def handle_load_position(self, location, position):
        return position

    def __save__(self):
        return ()

    @classmethod
    def __load__(cls, location):
        return cls()


class SavableRandom(Savable):
    def handle_load_position(self, location, position):
        chunk, position = location.choice_position(self)
        return position
