#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.point import Point

from engine.world.world_persistence import PersistentWorld
from engine.world.location import Location, near_cords
from engine.events import Event
from engine.enginelib.meta import DynamicObject, StaticObject


from random import randrange
from weakref import proxy
from collections import defaultdict
from time import time
import imp



class MetaWorld(PersistentWorld):
    "базовый класс карты"
    monster_count = 0
    
    def __init__(self, game, name):
        PersistentWorld.__init__(self, name)
        self.game = game
        self.name = name
        
        
        self.teleports = [Point(self.size/2, self.size/2)]
        
        self.location_size = self.size/LOCATIONSIZE +1
        
        self.tiles = defaultdict(lambda: set())
        
        self.players = {}
        
        self.locations = []
        self.active_locations = {}
        
        self.create_locations()
        self.create_links()


        init = imp.load_source('init', WORLD_PATH %name + 'init.py')
        self.generate_func = init.generate
        self.init_func =  init.init
    
    def start(self):
        result = self.load_objects()
        if not result:
            self.generate_func(self)
        self.init_func(self)

        

    
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

    def add_object(self, player):
        self.players[player.name] = proxy(player)

    def pop_object(self, player):
        name = player.name
        player.location.pop_object(player)
        if name in self.players:
            del self.players[name]

    
    def new_object(self, player):
        player.world = self
        player.handle_creating()
        
        location = self.get_location(player.position)
        location.add_object(player)
        player.location = location
        
        cord = player.position/TILESIZE
        self.add_to_tile(player, cord)
        
        self.game.new_object(player)
        self.add_object(player)

    def remove_object(self, player):
        player.location.pop_object(player)
        self.pop_from_tile(player, player.cord)
        self.pop_object(player)
        self.game.remove_object(player)


    
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
    
    def change_location(self, player, prev_loc, cur_loc):
        "если локация объекта изменилась, то удалитьйф ссылку на него из предыдущей локации и добавить в новую"
        pi, pj = prev_loc.get()
        prev_location = self.locations[pi][pj]
        ci, cj = cur_loc.get()
        if 0<ci<self.location_size and 0<cj<self.location_size :
            
            cur_location = self.locations[ci][cj]
                            
            prev_location.pop_object(player)
            cur_location.add_object(player)
            
            
            player.location = cur_location
            
            for related in player.related_objects:
                related.location = cur_location
        else:
            return prev_location
    
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

    def get_near_cords(self, i,j):
        "возвращает список соседних тайлов"
        insize = lambda i,j: 0<i<self.size and 0<j<self.size
        cords = [(i+ni, j+nj) for ni,nj in near_cords if insize(i+ni, j+nj)]
        return cords
    
    def add_to_tile(self, player, cur_cord):
        self.tiles[cur_cord].add(player)
        
    def pop_from_tile(self, player, cur_cord):
        tile = self.tiles[cur_cord]
        if player in tile:
            tile.remove(player)
    
    def update_tiles(self, player, prev_cord, cur_cord):
        if player in self.tiles[prev_cord]:
            self.tiles[prev_cord].remove(player)
        self.tiles[cur_cord].add(player)
    
        
    
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
        raise BaseException('world[%s].choice_position: no place for %s' % (self.name, player))
    
    def handle_over_range(self, player, position):
        pass
    
    
    
    def create_object(self, n, object_type):
        n = int(n/WORLD_MUL)
        for i in xrange(n):
            position = self.choice_position(object_type, self.size/2, ask_player = True)
            name = object_type.__name__
            
            monster = object_type('%s_%s' % (name, self.game.monster_count) , position)
            
            self.new_object(monster)
            
            self.game.monster_count+=1
    
    def create_item(self, n, object_type):
        n = int(n/WORLD_MUL)
        for i in xrange(n):
            position = self.choice_position(object_type, self.size/2, ask_player = True)
            
            item = object_type(position)
            
            self.new_object(item)
    
    def resize(self,cord):
        if 0<=cord<=self.size:
            return cord
        else:
            if cord>self.size:
                return self.size
            else:
                return 0
                
    
    
    


        
            
                


