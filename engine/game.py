#!/usr/bin/env python
# -*- coding: utf-8 -*-
#разделяемое состояние всех объектов игры
from config import *

from random import randrange
from weakref import proxy
from collections import defaultdict

from share.mathlib import Point, NullPoint
from game_lib import Event, ObjectContainer
from engine_lib import StaticObject, Guided
from world import World
from location import Location

        
class __GameSingleton():
    "синглтон игрового движка - хранит карту, все объекты, события и предоставляет доступ к ним"
    def __init__(self):
        self.players = {}
        self.guided_players = {}
        self.event_counter = 0 #счетчик событий для id события
        self.ball_counter = 0 #счетчик снарядов
        
        self.world = World(self)
        
        self.size = self.world.size
        print 'GameSingleton init'
    
    def generate_locations(self):
        self.locations = {}
        I = self.size/LOCATIONSIZE
        J = self.size/LOCATIONSIZE
        for i in range(I):
            for j in range(J):
                cord = Point(i,j)
                location = Location(cord)
                self.locations[cord] = location


    def add_event(self, event):
        "добавляет событие в локацию"
        loc_cord = self.location_cord(event.position)
        self.locations[loc_cord].add_event(event)
    
    def add_static_event(self, event):
        "добавляет событие в локацию"
        loc_cord = self.location_cord(event.position)
        self.locations[loc_cord].add_static_event(event)
        
    
    def move_object(self, player):
        "реакция на передвижение объекта - обновить данные локаций"
        prev_loc = self.location_cord(player.prev_position)
        cur_loc = self.location_cord(player.position)
        if cur_loc!=prev_loc:
            #перемещаем объект из прошлй локации в новую
            self.locations[prev_loc].remove_object(player.name)
            
            self.locations[cur_loc].add_object(player)
            
            
    
    def location_cord(self, position):
        "возвращает координаты локации для данной позиции"
        if position.x<0 or position.y<0:
            print 'INVALID POSITION', position
        return position/TILESIZE/LOCATIONSIZE
        
    def get_location(self, position):
        "возвращает локацию из окружающих локаций"
        loc_cord = self.location_cord(position)
        cords = [cord for cord in
                (loc_cord+Point(-1,1), loc_cord+Point(0,1), loc_cord+Point(1,1),
                loc_cord+Point(-1,0),  loc_cord, loc_cord+Point(1,0),
                loc_cord+Point(-1,-1), loc_cord+Point(0,-1), loc_cord+Point(1,-1))]
        cords = [cord for cord in cords if self.world.loc_cord_valid(cord)]
        return sum([self.locations[cord] for cord in cords], ObjectContainer())
        
    def new_object(self, player):
        "оповестить всех о новом объекте"
        self.players[player.name] = player
        
        if isinstance(player, Guided):
            self.guided_players[player.name] = proxy(player)
        
        loc_cord = self.location_cord(player.position)
        self.locations[loc_cord].add_object(player)
        
        
       
    
        
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
    
    def clear_events(self):
        [location.clear_events() for location in self.locations.values()]
    
    def remove_object(self, name, force = False):
        "удаляет игровые объекты, если метод remove вернул False то откладывет удаление объекта"
        player = self.players[name]
        result = player.remove()
        if result or force:
            loc_cord = self.location_cord(player.position)
            self.locations[loc_cord].remove_object(name)
            if isinstance(player, Guided):
                del self.guided_players[player.name]
            del self.players[name]
        else:
            self.players[name].REMOVE = False

game = __GameSingleton()
game.generate_locations()

import location
location.init()

import engine_lib
engine_lib.init()
