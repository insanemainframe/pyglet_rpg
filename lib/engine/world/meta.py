#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.point import Point

from engine.world.world_persistence import PersistentWorld
from engine.world.chunk import Chunk, near_cords
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
        
        self.chunk_size = self.size/CHUNK_SIZE +1
        
        self.tiles = defaultdict(list)
        
        self.players = {}
        
        self.chunks = []
        self.active_chunks = {}
        
        self.create_chunks()
        self.create_links()


        init = imp.load_source('init', WORLD_PATH %name + 'init.py')
        self.generate_func = init.generate
    
    def start(self):
        result = self.load_objects()
        if not result:
            self.generate_func(self)

        

    
    def create_chunks(self):
        "создает локации"
        for i in xrange(self.chunk_size):
            chunks = []
            for j in xrange(self.chunk_size):
                chunks.append(Chunk(self, i,j))
            self.chunks.append(chunks)
    
    def create_links(self):
        "создает ссылки в локациях"
        for row in self.chunks:
            for chunk in row:
                chunk.create_links()

    def add_object(self, player):
        self.players[player.name] = proxy(player)

    def pop_object(self, player):
        name = player.name
        player.chunk.pop_object(player)
        if name in self.players:
            del self.players[name]

    
    def new_object(self, player):
        player.world = self
        player.handle_creating()
        
        chunk = self.get_chunk(player.position)
        chunk.add_object(player)
        player.chunk = chunk
        
        cord = player.position/TILESIZE
        self.add_to_tile(player, cord)
        
        self.game.new_object(player)
        self.add_object(player)

    def remove_object(self, player):
        player.chunk.pop_object(player)
        self.pop_from_tile(player, player.cord)
        self.pop_object(player)
        self.game.remove_object(player)


    
    def add_event(self, name, object_type, position, vector, action, args=(), timeout=0, ):
        "добавляет событие"
        event = Event(name, object_type, position, action, args, timeout)
        
        
        i,j = self.get_loc_cord(position).get()
        try:
            self.chunks[i][j].add_event(event)
        except IndexError:
            print('chunk IndexError', i,j)
    
        if vector:
            alt_position = position+vector
            event = Event(name, object_type, alt_position, action, args, timeout)
            i,j = self.get_loc_cord(alt_position).get()
            try:
                self.chunks[i][j].add_event(event)
            except IndexError:
                print('chunk IndexError %s[%s:%s] %s' (self.name, i,j, name))
    
    def change_chunk(self, player, prev_loc, cur_loc):
        "если локация объекта изменилась, то удалитьйф ссылку на него из предыдущей локации и добавить в новую"
        pi, pj = prev_loc.get()
        prev_chunk = self.chunks[pi][pj]
        ci, cj = cur_loc.get()
        if 0<ci<self.chunk_size and 0<cj<self.chunk_size :
            
            cur_chunk = self.chunks[ci][cj]
                            
            prev_chunk.pop_object(player)
            cur_chunk.add_object(player)
            
            
            player.chunk = cur_chunk
            
            for related in player.related_objects:
                related.chunk = cur_chunk
        else:
            return prev_chunk
    
    def get_loc_cord(self, position):
        "возвращает координаты локации для заданой позиции"
        return position/TILESIZE/CHUNK_SIZE
    
    
    def get_chunk(self, position):
        "возвращает слокацию"
        
        i,j = (position/TILESIZE/CHUNK_SIZE).get()
        try:
            return self.chunks[i][j]
        except IndexError as Error:
            print('Warning: invalid chunk cord %s[%s:%s]' % (self.name,i,j))
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
        self.tiles[cur_cord.get()].append(player)
        
    def pop_from_tile(self, player, cur_cord):
        tile = self.tiles[cur_cord.get()]
        if player in tile:
            tile.remove(player)
    
    def update_tiles(self, player, prev_cord, cur_cord):
        tile = self.tiles[prev_cord.get()]
        if player in tile:
            tile.remove(player)

        self.tiles[cur_cord.get()].append(player)
    
        
    
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
                        chunk = self.get_chunk(position)
                        exp = ask_player and player.choice_position(self, chunk, i ,j)
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
                
    
    
    


        
            
                


