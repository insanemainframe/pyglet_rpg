#!/usr/bin/env python
# -*- coding: utf-8 -*-
#разделяемое состояние всех объектов игры
from config import *

from random import randrange
from weakref import proxy

#game = None

from share.mathlib import Point, NullPoint
from game_lib import ObjectContainer, EventsContainer
        
        

        
class __GameSingleton(ObjectContainer, EventsContainer):
    "синглтон игрового движка - хранит карту, все объекты, события и предоставляет доступ к ним"
    def __init__(self):
        ObjectContainer.__init__(self)
        EventsContainer.__init__(self)
    
    def start(self):
        from world import World, UnderWorld

        self.world = World(proxy(self))
        
        self.world.start()
        print 'GameSingleton init'
        self.worlds = {'ground': World, 'underground':UnderWorld}
        for world in self.world.values:
            world.start()

      
    def change_location(self, name, prev_loc, cur_loc):
        "если локация объекта изменилась, то удалитьйф ссылку на него из предыдущей локации и добавить в новую"
        pi, pj = prev_loc
        ci, cj = cur_loc
        prev_location = self.world.locations[pi][pj]
        cur_location = self.world.locations[ci][cj]
                        
        prev_location.pop_player(name)
        cur_location.add_player(self.players[name])
        
        return proxy(self.world.locations[ci][cj])
    
    def get_active_locations(self):
        "список активных локаций"
        return self.world.active_locations.values()
    
    def get_location(self, position):
        "возвращает список ближайших локаций"
        i,j = (position/TILESIZE/LOCATIONSIZE).get()
        return self.world.locations[i][j]
    
    def get_loc_cord(self, position):
        "коордианты локации позиции"
        return self.world.get_loc_cord(position)
        
        
    def choice_position(self, player, radius=7, start=False):
        "выбирает случайную позицию, доступную для объекта"
        return self.world.choice_position(player, radius, start)
        
    

            


game = __GameSingleton()

import game_lib
game_lib.init()
import world
world.init()

