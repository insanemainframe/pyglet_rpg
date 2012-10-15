#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.mathlib import Point

from worldmaps.mapgen import load_map
from engine.location import Location, near_cords
from engine.singleton_lib import Event
from engine import engine_lib


from weakref import proxy
from random import randrange

class MetaWorldTools:
    def create_object(self, n, object_type):
        for i in xrange(n):
            position = self.choice_position(object_type, self.size/2, ask_player = True)
            name = object_type.__name__
            
            monster = object_type('%s_%s' % (name, self.game.monster_count) , position)
            
            self.new_object(monster)
            
            self.game.monster_count+=1
    
    def create_item(self, n, object_type):
        for i in xrange(n):
            position = self.choice_position(object_type, self.size/2, ask_player = True)
            
            item = object_type(position)
            
            self.new_static_object(item)
    
    def resize(self,cord):
        if 0<=cord<=self.size:
            return cord
        else:
            if cord>self.size:
                return self.size
            else:
                return 0
    
            


class MetaWorld(MetaWorldTools):
    "базовый класс карты"
    monster_count = 0
    def __init__(self, game, name, mapname):
        self.game = game
        self.name = name
        self.mapname = mapname
        
        
        self.map, self.size, self.background = load_map(mapname)
        
        self.teleports = [Point(self.size/2, self.size/2)]
        
        self.location_size = self.size/LOCATIONSIZE +1
        
        
        self.locations = []
        self.active_locations = {}
        
        self.create_locations()
        self.create_links()
        data = (mapname, self.size, self.size, self.background, len(self.locations), len(self.locations[0]))
        print('creating world "%s" %sx%s background %s locations %sx%s' % data)
    
    def create_locations(self):
        "создает локации"
        for i in xrange(self.location_size):
            locations = []
            for j in xrange(self.location_size):
                locations.append(Location(self, i,j))
            self.locations.append(locations)
    
    def create_links(self):
        "создает ссылки в локациях"
        for row in self.locations:
            for location in row:
                location.create_links()
    
    def new_object(self, player):
        self.game.new_object(self.name, player)
        
    def new_static_object(self, player):
        self.game.new_static_object(self.name, player)
        
    
    
    def add_static_event(self, name, object_type, position, action, args=(), timeout=0):
        "добавляет со9-бытие статического объекта"
        event = Event(name, object_type, position, action, args, timeout)
        
        i,j = self.get_loc_cord(position).get()
        self.locations[i][j].add_static_event(event)
    
    def add_event(self, name, object_type, position, vector, action, args=(), timeout=0, ):
        "добавляет событие"
        event = Event(name, object_type, position, action, args, timeout)
        
        
        i,j = self.get_loc_cord(position).get()
        try:
            self.locations[i][j].add_event(event)
        except IndexError:
            print('location IndexError', i,j)
    
        if vector:
            alt_position = position+vector
            event = Event(name, object_type, alt_position, action, args, timeout)
            i,j = self.get_loc_cord(alt_position).get()
            try:
                self.locations[i][j].add_event(event)
            except IndexError:
                print('location IndexError %s[%s:%s] %s' (self.name, i,j, name))
    
    def change_location(self, name, prev_loc, cur_loc):
        "если локация объекта изменилась, то удалитьйф ссылку на него из предыдущей локации и добавить в новую"
        pi, pj = prev_loc.get()
        prev_location = self.locations[pi][pj]
        ci, cj = cur_loc.get()
        if 0<ci<self.location_size and 0<cj<self.location_size :
            
            cur_location = self.locations[ci][cj]
                            
            prev_location.pop_player(name)
            cur_location.add_player(self.game.players[name].player)
            
            return proxy(self.locations[ci][cj])
        else:
            return proxy(prev_location)
    
    def get_loc_cord(self, position):
        "возвращает координаты локации для заданой позиции"
        return position/TILESIZE/LOCATIONSIZE
    
    
    def get_location(self, position):
        "возвращает слокацию"
        
        i,j = (position/TILESIZE/LOCATIONSIZE).get()
        try:
            return self.locations[i][j]
        except IndexError as Error:
            print('Warning: invalid location cord %s[%s:%s]' % (self.name,i,j))
            raise Error
    
    def get_near_tiles(self, i,j):
        "возвращает список соседних тайлов"
        insize = lambda i,j: 0<i<self.size and 0<j<self.size
        cords = [(i+ni, j+nj) for ni,nj in near_cords if insize(i+ni, j+nj)]
        tiles = [self.map[i][j] for i,j in cords]
        return tiles
        
    
    def choice_position(self, player, radius=7, start=False, ask_player = False):
        "выбирает случайную позицию, доступную для объекта"
        if not start:
            start = Point(self.size/2,self.size/2)
        else:
            start = start/TILESIZE
        lim = 1000
        counter = 0
        cords = set()
        timeout = self.size**2
        
        while len(cords)<timeout:
            
            position = start +Point(randrange(-radius, radius), randrange(-radius, radius))
            cord = position
            if cord not in cords:
                cords.add(cord)
                i,j =  cord.get()
                if 1<i<self.size-1 and 1<j<self.size-1:
                    
                    if not self.map[i][j] in player.BLOCKTILES:
                        #проверяем, подходит ли клетка объекту
                        position = position*TILESIZE
                        location = self.get_location(position)
                        exp = ask_player and player.choice_position(self, location, i ,j)
                        if counter>1000 or exp:
                            shift = Point(randrange(TILESIZE-1),randrange(TILESIZE-1))
                            return position+shift
            counter+=1
            if counter>lim:
                lim*=2
                if radius<self.size/2:
                    radius = int(radius*1.5)
        raise Exception('world[%s].choice_position: no place for %s' % (self.name, player))
    
    def handle_over_range(self, player, position):
        pass
    

