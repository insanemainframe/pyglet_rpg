#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.mathlib import Point, NullPoint
from game_objects import *

from worldmaps.mapgen import load_map
from engine.location import Location

from weakref import proxy

engine_lib = None

class MetaWorldTools:
    def create_object(self, n, object_type):
        for i in range(n):
            position = self.choice_position(object_type, self.size)
            name =object_type.__name__
            monster = object_type('%s_%s' % (name, MetaWorld.monster_count) , self.mapname, position)
            MetaWorld.monster_count+=1
    
    def create_item(self, n, object_type):
        for i in range(n):
            position = self.choice_position(object_type, self.size)
            monster = object_type(self.name, position)

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
        for i in range(self.location_size):
            locations = []
            for j in range(self.location_size):
                locations.append(Location(self, i,j))
            self.locations.append(locations)
    
    def create_links(self):
        for row in self.locations:
            for location in row:
                location.create_links()
    
    def change_location(self, name, prev_loc, cur_loc):
        "если локация объекта изменилась, то удалитьйф ссылку на него из предыдущей локации и добавить в новую"
        pi, pj = prev_loc
        ci, cj = cur_loc
        prev_location = self.locations[pi][pj]
        cur_location = self.locations[ci][cj]
                        
        prev_location.pop_player(name)
        cur_location.add_player(self.game.players[name].player)
        
        return proxy(self.locations[ci][cj])
    
    def get_loc_cord(self, position):
        return (position/TILESIZE/LOCATIONSIZE).get()
    
    
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
        while 1:
            
            position = start +Point(randrange(-radius, radius), randrange(-radius, radius))
            i,j = position.get()
            if 0<i<self.size and 0<j<self.size:
                if not self.map[i][j] in player.BLOCKTILES:
                    position = position*TILESIZE
                    return position
            counter+=1
            if counter>lim:
                print 'lim!'
                lim*=2
                radius = int(radius*1.5)
                if radius>self.size/2:
                    raise Exception('world[%s].choice_position: no place for %s' % (self.name, player))
    
    

class World(MetaWorld):
    "поверхность"
    def __init__(self, name, game):
        MetaWorld.__init__(self, game, name, 'ground')
    
    def start(self):
        self.create_item(100, GetTeleport(Cave, 'underground'))
        self.create_item(200, Stone)
        self.create_item(200, Mushroom)
        self.create_item(200, Plant)
        self.create_item(200, WaterFlower)
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
        
        self.create_item(200, Stone)
        self.create_item(200, Mushroom)
        self.create_item(200, Stone)
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
        
        self.create_item(200, Stone)
        self.create_item(200, Mushroom)
        self.create_item(200, Stone)
        self.create_item(50, Rubble)
        
        self.create_object(100, Zombie)
        self.create_object(20, Lych)
        self.create_object(20, Ghast)
        self.create_object(20, Cat)



########################################################################


        
def init():
    global engine_lib
    import engine_lib
    

