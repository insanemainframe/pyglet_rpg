#!/usr/bin/env python
# -*- coding: utf-8 -*-
#разделяемое состояние всех объектов игры
from config import *

from random import randrange
from weakref import proxy
from collections import defaultdict

from share.mathlib import Point, NullPoint
from maplib import World
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


    def add_event(self, name, position, vector, action, args=(), timeout=0):
        "добавляет событие"
        if action:
            map_position = (position/TILESIZE).get()
            object_type = self.players[name].__class__.__name__
            
            event = Event(name, object_type, position, action, args, timeout)
            if isinstance(self.players[name], StaticObject):
                self.static_events[map_position].add(event)
                if timeout:
                    self.timeout_static_events[map_position].add(event)
            else:
                self.events[map_position].add(event)
                if timeout:
                    self.timeout_events[map_position].add(event)
                if vector:
                    alt_key = (position+vector/TILESIZE).get()
                    self.events[alt_key].add(event)
                    if timeout:
                        self.timeout_events[alt_key].add(event)
    
    def move_object(self, player):
        "реакция на передвижение объекта - обновить данные локаций"
        pass
    
    def get_locations(self, position):
        "возвращает список ближайших локаций"
        loc_cord = position/LOCATIONSIZE
        cords = [cord.get() for cord in
                (loc_cord+Point(-1,1), loc_cord+Point(0,1), loc_cord+Point(1,1),
                loc_cord+Point(-1,0),  loc_cord, loc_cord+Point(1,0),
                loc_cord+Point(-1,-1), loc_cord+Point(0,-1), loc_cord+Point(1,-1))]
        
        return [self.locations[i][j] for i,j in cords]
        
    def new_object(self, player):
        "оповестить всех о новом объекте"
        self.players[player.name] = player
        #
        self.new_object_proxy(player)
        #добавляем обновление
        key = (player.position/TILESIZE).get()
        if not isinstance(player, StaticObject):
            self.add_event(player.name, player.position, False, 'exist', [NullPoint.get()])
    
    
    def new_object_proxy(self, player):
        "создает ссылки на объект в специальных списках объектов"
        name = player.name
        if isinstance(player, Guided):
            self.guided_players[name] = proxy(player)
        if isinstance(player, Solid):
            self.solid_objects[name] = proxy(player)
        if isinstance(player, StaticObject):
            cord = (player.position/TILESIZE).get()
            self.static_objects[cord][name] = proxy(player)
    
    def remove_object_proxy(self, player):
        "удаляет ссылки на объект из списков"
        name = player.name
        if isinstance(player, Guided):
            del self.guided_players[name]
        if isinstance(player, Solid):
            del self.solid_objects[name]
        if isinstance(player, StaticObject):
            cord = (player.position/TILESIZE).get()
            del self.static_objects[cord][name]
        
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
        
    def clear(self):
        "удаляем объекты отмеченыне меткой REMOVE"
        remove_list = []
        for name in self.players:
            if self.players[name].REMOVE:
                remove_list.append(name)
        #
        for name in remove_list:
            self.remove_object(name)
    
    def remove_object(self, name, force = False):
        "удаляет игровые объекты, если метод remove вернул False то откладывет удаление объекта"
        result = self.players[name].remove()
        if result or force:
            player = self.players[name]
            self.remove_object_proxy(player)
            del self.players[name]
        else:
            self.players[name].REMOVE = False


game = __GameSingleton()
from engine_lib import Solid, Guided, StaticObject
