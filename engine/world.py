#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.mathlib import Point

from engine.game_objects import *
from worldmaps.mapgen import load_map
from engine.location import Location
from engine.singleton_lib import Event


from weakref import proxy

engine_lib = None

class MetaWorldTools:
    def create_object(self, n, object_type):
        for i in xrange(n):
            position = self.choice_position(object_type, self.size/2)
            name = object_type.__name__
            monster = object_type('%s_%s' % (name, MetaWorld.monster_count) , self.mapname, position)
            MetaWorld.monster_count+=1
    
    def create_item(self, n, object_type):
        for i in xrange(n):
            position = self.choice_position(object_type, self.size/2)
            monster = object_type(self.name, position)
    
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
        
        self.location_size = self.size/LOCATIONSIZE
        if self.location_size*LOCATIONSIZE<self.size:
            self.location_size+=1
        
        
        self.locations = []
        self.active_locations = {}
        
        self.create_locations()
        self.create_links()
        data = (mapname, self.size, self.size, self.background, len(self.locations), len(self.locations[0]))
        print 'creating world "%s" %sx%s background %s locations %sx%s' % data
    
    def create_locations(self):
        for i in xrange(self.location_size):
            locations = []
            for j in xrange(self.location_size):
                locations.append(Location(self, i,j))
            self.locations.append(locations)
    
    def create_links(self):
        for row in self.locations:
            for location in row:
                location.create_links()
    
    def add_static_event(self, name, object_type, position, action, args=(), timeout=0):
        "добавляет со9-бытие статического объекта"
        event = Event(name, object_type, position, action, args, timeout)
        
        i,j = self.get_loc_cord(position).get()
        self.locations[i][j].add_static_event(event)
    
    def add_event(self, name, object_type, position, vector, action, args=(), timeout=0, ):
        "добавляет событие"
        event = Event(name, object_type, position, action, args, timeout)
        
        
        i,j = self.get_loc_cord(position).get()
        self.locations[i][j].add_event(event)
    
        if vector:
            alt_position = position+vector
            event = Event(name, object_type, alt_position, action, args, timeout)
            i,j = self.get_loc_cord(alt_position).get()
            try:
                self.locations[i][j].add_event(event)
            except IndexError:
                pass
    
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
        return position/TILESIZE/LOCATIONSIZE
    
    
    def get_location(self, player):
        "возвращает слокацию"
        position = player.position
        
        i,j = (position/TILESIZE/LOCATIONSIZE).get()
        return self.locations[i][j]
    
    def get_location_static(self, player):
        "возвращает слокацию"
        position = player.position
        i,j = (position/TILESIZE/LOCATIONSIZE).get()
        return self.locations[i][j]
    
    
    
    
    def choice_position(self, player, radius=7, start=False):
        "выбирает случайную позицию, доступную для объекта"
        if not start:
            start = Point(self.size/2,self.size/2)
        else:
            start = start/TILESIZE
        lim = 1000
        counter = 0
        cords = set()
        
        while len(cords)<self.size**2:
            
            position = start +Point(randrange(-radius, radius), randrange(-radius, radius))
            cord = position
            if cord not in cords:
                cords.add(cord)
                i,j =  cord.get()
                if 1<i<self.size-1 and 1<j<self.size-1:
                    
                    if not self.map[i][j] in player.BLOCKTILES:
                        position = position*TILESIZE
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
    
    

class World(MetaWorld):
    "поверхность"
    def __init__(self, name, game):
        MetaWorld.__init__(self, game, name, 'ground')
    
    def start(self):
        self.create_item(200, GetTeleport(Cave, 'underground'))
        
        self.create_item(500, Stone)
        self.create_item(200, Mushroom)
        self.create_item(500, Plant)
        self.create_item(5000, Flower)
        self.create_item(500, WaterFlower) 
        self.create_item(300, AloneTree)
        
        self.create_object(200, Zombie)
        self.create_object(50, Lych)
        self.create_object(50, Ghast)
        self.create_object(50, Cat)




class UnderWorld(MetaWorld):
    "подземелье"
    def __init__(self, name,  game):
        MetaWorld.__init__(self, game, name,  'underground')
    
    def start(self):
        self.create_item(200, GetTeleport(Stair,'ground'))
        self.create_item(200, GetTeleport(DownCave, 'underground2'))
        
        self.create_item(600, Mushroom)
        self.create_item(600, Stone)
        self.create_item(50, Rubble)
        
        self.create_object(100, Zombie)
        self.create_object(20, Lych)
        self.create_object(20, Ghast)
        self.create_object(20, Cat)

class UnderWorld2(MetaWorld):
    "подземелье"
    def __init__(self, name,  game):
        MetaWorld.__init__(self, game, name,  'underground2')
    
    def start(self):
        self.create_item(200, GetTeleport(UpStair,'underground'))
        
        self.create_item(600, Stone)
        self.create_item(600, Mushroom)
        self.create_item(200, Stone)
        self.create_item(50, Rubble)
        
        self.create_object(100, Zombie)
        self.create_object(30, Lych)
        self.create_object(30, Ghast)
        self.create_object(30, Cat)




        
def init():
    global engine_lib
    import engine_lib
    

