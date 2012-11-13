#!/usr/bin/env python
# -*- coding: utf-8 -*-
#разделяемое состояние всех объектов игры
from config import *


from weakref import proxy, ProxyType
from random import  choice
from collections import OrderedDict

from share.mathlib cimport Point

from engine.enginelib import meta
from engine.enginelib.meta import DynamicObject, StaticObject
from engine.world.meta import MetaWorld


        
class __GameSingleton(object):
    "синглтон игрового движка - хранит карты, все объекты, и предоставляет доступ к ним"


    def __init__(self):
        self.guided_players = {} #управляемые игроки
        self.players = {}
        self.static_objects = {}
        
        self.monster_count = 0
        self.guided_changed = False

        self.worlds = {}

    
    def start(self):
        print('\n Engine initialization...')
        
        self.worlds['ground'] = MetaWorld(self, 'ground')
        self.worlds['underground'] = MetaWorld(self, 'underground')
        self.worlds['underground2'] = MetaWorld(self, 'underground2')
        
        self.mainworld = self.worlds['ground']
        
        for world in self.worlds.values():
            world.start()
            world.save(True)
        
        print('\n Engine initialization complete. \n')
    
        
    def new_object(self, player):
        "создает динамический объект"
        if isinstance(player, meta.DynamicObject):
            self.players[player.name] = player
             
            if isinstance(player, meta.Guided):
                self.guided_players[player.name] = proxy(player)
                
        else:
            self.static_objects[player.name] = player
        
    
    
    def remove_object(self, player):
        cdef str name

        name = player.name
        if name in self.players or name in self.static_objects:
            if isinstance(player, DynamicObject):
                player = self.players[name]
                del self.players[name]
            else:
                player = self.static_objects[name]
                del self.static_objects[name]
            
            player.handle_remove()
            player.world.remove_object(player)
    


    def remove_guided(self, str name):
        player = self.guided_players[name]
        
        location = player.location
        
        location.remove_object(player, True)
        
        del self.guided_players[name]
        try:
            self.remove_object(player)
        except:
            pass
    
    def add_to_remove(self, player, force):
        location = player.location
        location.add_to_remove(player, force)


    def change_world(self, player, world, Point new_position = Point(0,0)):
        "переметить объект из одного мира в другой"
        cdef int li, lj
        cdef Point position


        prev_world = player.world
        new_world = self.worlds[world]
        
        prev_world.remove_object(player)
        player.location.pop_object(player)
        
        teleport_point = choice(new_world.teleports)
        if not new_position:
            new_position = new_world.choice_position(player, 5, teleport_point)
        li, lj = (new_position/TILESIZE/LOCATIONSIZE).get()
        
        

        new_location = new_world.locations[li][lj]
        new_location.add_object(player)
        new_world.add_object(player)

        
        player.world = proxy(new_world)
        
        
        player.location = proxy(new_location)
        player.set_position(new_position)
        player.flush()
        
        
        player.world_changed = True
        player.cord_changed = True
        if isinstance(player, DynamicObject):
            player.flush()
        #обновляем хэш объекта
        player.regid()
        
        for slave in player.slaves.copy():
            position = new_world.choice_position(slave, 3, new_position)
            self.change_world(slave, world, position)
        
        for related in player.related_objects:
            related.world = proxy(new_world)
            related.location = proxy(new_location)
    
    def get_active_locations(self):
        "список активных локаций"
        lsum = sum
        return lsum([world.active_locations.values() for world in self.worlds.values()], [])
    
    def get_guided_list(self, str self_name):
        f = lambda cont:  ('(%s)'% player.name if player.name==self_name else player.name, player.kills)
        return [f(player) for player in self.guided_players.values()]
    
    def save(self):
        for world in self.worlds.values():
            world.save()

game = __GameSingleton()


