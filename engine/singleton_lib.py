#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.mathlib import *

from collections import defaultdict
from weakref import proxy

from engine import engine_lib

class Event:
    def __init__(self, name, object_type, position, action, args, timeout=0):
        hash(args)
        self.name = name
        self.object_type = object_type
        self.position = position
        self.action = action
        self.args = tuple(args)
        self.timeouted = timeout
    
    def get_tuple(self):
        return self.name, self.object_type, self.position.get(), self.timeouted, self.action, self.args
    
    def update(self):
        self.timeouted-=1
        return bool(self.timeouted)
    
    def __hash__(self):
        return hash((self.name, self.action, self.args))
    
    def __eq__(self, another):
        return another.__hash__()==self.__hash__()
    
    def __ne__(self, another):
        return another.__hash__()!=self.__hash__()
        
    
    def __str__(self):
        return "Event: %s %s %s <%s>" % (self.object_type,self.name, self.position, self.action) 

class ObjectItem:
    def __init__(self, player, world):
        if isinstance(player, engine_lib.GameObject) and isinstance(world, str):
            self.player = player
            self.world = world
            self.name = player.name
        else:
            raise TypeError('%s, %s' % (str(player), str(world)))
    
    

class ObjectContainer(object):
    "функционал игрового синглетона для упрвления объектами"
    def __init__(self):
        self.guided_players = {} #управляемые игроки
        self.players = {}
        self.static_objects = {}
        
        self.monster_count = 0
                    
    
    def new_object(self, world, player):
        "создает динамический объект"
        if isinstance(player, engine_lib.DynamicObject) and isinstance(world, str):
            self.players[player.name] = ObjectItem(player, world)
            
            
            ref = proxy(player)
             
            if isinstance(player, engine_lib.Guided):
                self.guided_players[player.name] = ref
                
            #
            world = self.worlds[world]
            player.world = proxy(world)
            player.handle_creating()
            
            location = world.get_location(player.position)
            location.add_player(ref)
            player.location = location
        else:
            raise TypeError('new_object: %s not DynamicObject instance or %s not str' % (player.name, world))
        
    
    def new_static_object(self, world,player):
        "создает статический оъект"
        if isinstance(player, engine_lib.StaticObject):
            ref = proxy(player)
            self.static_objects[player.name] = ObjectItem(player, world)
            
            world = self.worlds[world]
            player.world = proxy(world)
            player.handle_creating()
            
            location = world.get_location(player.position)
            location.add_static_object(ref)
            player.location = location
            
        else:
            raise TypeError('new_static_object: %s not StaticObject instance' % player.name)
    
    def remove_player_from_list(self, name):
        self.players[name].player.handle_remove()
        del self.players[name]
    
    def remove_static_object_from_list(self, name):
        del self.static_objects[name]
    
    def remove_guided(self, name):
        player = self.guided_players[name]
        
        location = player.location
        
        location.remove_player(name, True)
        
        del self.guided_players[name]
    
    def add_to_remove(self, player, force):
         location = player.location
         location.add_to_remove(player.name, force)
    
    def add_to_remove_static(self, player, force):
         location = player.location
         location.add_to_remove_static(player.name, force)
    
    def get_world(self, name):
        return self.worlds[self.players[name].world]
    
    def get_world_static(self, name):
        return self.static_objects[name].world
    
    
        

        
    


