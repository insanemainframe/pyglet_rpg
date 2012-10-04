#!/usr/bin/env python
# -*- coding: utf-8 -*-
#разделяемое состояние всех объектов игры
from config import *

from random import randrange
from weakref import proxy
from collections import defaultdict

from share.mathlib import Point, NullPoint
from world import World
from game_lib import ObjectContainer, Event, Eventlist
         
        
class __GameSingleton(ObjectContainer):
    "синглтон игрового движка - хранит карту, все объекты, события и предоставляет доступ к ним"
    def __init__(self):
        ObjectContainer.__init__(self)
        self.event_counter = 0 #счетчик событий для id события
        self.ball_counter = 0 #счетчик снарядов
        
        self.world = World()
        
        
        
        self.size = self.world.size
        print 'GameSingleton init'


    def add_event(self, name, object_type, position, vector, action, args=(), timeout=0, delayed=False):
        "добавляет событие"
        map_position = (position/TILESIZE).get()
        i,j = self.world.get_loc_cord(position)
        
        event = Event(name, object_type, position, action, args, timeout, delayed)

        self.events[map_position].add(event)
        self.world.locations[i][j].new_event()
        if timeout:
            self.timeout_events[map_position].add(event)
        if vector:
            alt_key = (position+vector/TILESIZE).get()
            self.events[alt_key].add(event)
            if timeout:
                self.timeout_events[alt_key].add(event)
    
    def add_static_event(self, name, object_type, position, action, args=(), timeout=0, delayed=False):
        map_position = (position/TILESIZE).get()
        i,j = self.world.get_loc_cord(position)
        
        event = Event(name, object_type, position, action, args, timeout, delayed)
        
        self.static_events[map_position].add(event)
        self.world.locations[i][j].new_static_event()
        if timeout:
            self.timeout_static_events[map_position].add(event)
      
    def change_location(self, name, prev_loc, cur_loc):
        "если локация объекта изменилась, то удалитьйф ссылку на него из предыдущей локации и добавить в новую"
        pi, pj = prev_loc
        ci, cj = cur_loc
        prev_location = self.world.locations[pi][pj]
        cur_location = self.world.locations[ci][cj]
        
        player = self.players[name]
        
        prev_location.remove_player(player)
        cur_location.add_player(player)
    
    def get_location(self, position):
        "возвращает список ближайших локаций"
        i,j = (position/TILESIZE/LOCATIONSIZE).get()
        return self.world.locations[i][j]
    
    def get_loc_cord(self, position):
        "коордианты локации позиции"
        return self.world.get_loc_cord(position)
        
    def new_object(self, player):
        "создает динамический объект"
        if isinstance(player, DynamicObject):
            self.players[player.name] = player
            #
            i,j = self.world.get_loc_cord(player.position)
            self.world.locations[i][j].add_player(player)
            #
            self.new_object_proxy(player)
        else:
            raise TypeError('new_object: %s not DynamicObject instance' % player.name)
        
    
    def new_static_object(self, player):
        "создает статический оъект"
        if isinstance(player, StaticObject):
            self.static_objects[player.name] = player
            i,j = self.world.get_loc_cord(player.position)
            self.world.locations[i][j].add_static_object(player)
            
            key = (player.position/TILESIZE).get()
            self.world.locations[i][j].new_static_event()
            
            object_type = player.__class__.__name__
            self.add_static_event(player.name, object_type, player.position, 'exist', (NullPoint.get(),))
        else:
            raise TypeError('new_static_object: %s not StaticObject instance' % player.name)
    
    def new_object_proxy(self, player):
        "создает ссылки на объект в специальных списках объектов"
        name = player.name
        if isinstance(player, Guided):
            self.guided_players[name] = proxy(player)
        if isinstance(player, Solid):
            self.solid_objects[name] = proxy(player)

    
    def remove_object_proxy(self, player):
        "удаляет ссылки на объект из списков"
        name = player.name
        if isinstance(player, Guided):
            del self.guided_players[name]
        if isinstance(player, Solid):
            del self.solid_objects[name]

        
    def choice_position(self, player, radius=7, start=False):
        "выбирает случайную позицию, доступную для объекта"
        if not start:
            start = Point(self.size/2,self.size/2)
        else:
            start = start/TILESIZE
        while 1:
            
            position = start +Point(randrange(-radius, radius), randrange(-radius, radius))
            i,j = position.get()
            if not self.world.map[i][j] in player.BLOCKTILES:
                position = position*TILESIZE
                return position
        
    def clear_players(self):
        "удаляем динамические объекты отмеченыне меткой REMOVE"
        remove_list = []
        for name in self.players:
            if isinstance(self.players[name], DynamicObject):
                if self.players[name].REMOVE:
                    remove_list.append(name)
            else:
                raise TypeError('clear_players %s not DynamicObject instance' % name)
        #
        for name in remove_list:
            self.remove_object(name)
    
    def clear_static(self):
        "удаляем статические объекты отмеченыне меткой REMOVE"
        remove_list = []
        for name in self.static_objects:
            if self.static_objects[name].REMOVE:
                remove_list.append(name)
        #
        for name in remove_list:
            self.remove_static_object(name)
    
    def remove_object(self, name, force = False):
        "удаляет динамические объекты, если метод remove вернул False то откладывет удаление объекта"
        result = self.players[name].remove()
        if result or force:
            player = self.players[name]
            position = player.position
            action = 'delay' if player.delayed else 'remove'
            object_type = player.__class__.__name__
            self.add_event(name, object_type, position, NullPoint, action, ())
            
            #
            i,j = self.world.get_loc_cord(player.position)
            self.world.locations[i][j].remove_player(player)
            #
            self.remove_object_proxy(player)
            del self.players[name]
        else:
            self.players[name].REMOVE = False
    
    def remove_static_object(self, name, force = False):
        "удаляет статические объекты, если метод remove вернул False то откладывет удаление объекта"
        result = self.static_objects[name].remove()
        if result or force:
            player = self.static_objects[name]
            position = player.position
            action = 'delay' if player.delayed else 'remove'
            object_type = player.__class__.__name__
            self.add_static_event(name, object_type, position, action, ())
            #
            i,j = self.world.get_loc_cord(position)
            self.world.locations[i][j].remove_static_object(player)
            #
            print 'remove_static_object', name
            del self.static_objects[name]
        else:
            self.static_objects[name].REMOVE = False
    

            


game = __GameSingleton()

import world
world.init()

from engine_lib import Solid, Guided, StaticObject, DynamicObject
    
