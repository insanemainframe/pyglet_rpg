#!/usr/bin/env python
# -*- coding: utf-8 -*-
#разделяемое состояние всех объектов игры
from config import *

from random import randrange, choice
from weakref import proxy


from share.mathlib import Point
from engine.singleton_lib import ObjectContainer, ObjectItem
        
        

        
class __GameSingleton(ObjectContainer):
    "синглтон игрового движка - хранит карты, все объекты, и предоставляет доступ к ним"
    def __init__(self):
        ObjectContainer.__init__(self)

    
    def start(self):
        from engine.world import World, UnderWorld, UnderWorld2


        
        print('Engine initialization...')
        
        self.worlds = {}
        self.worlds['ground'] = World('ground',proxy(self))
        self.worlds['underground'] = UnderWorld('underground', proxy(self))
        self.worlds['underground2'] = UnderWorld2('underground2', proxy(self))
        
        self.mainworld = self.worlds['ground']
        
        for world in self.worlds.values():
            print('world %s initialization' % world.name)
            world.start()
        
        print('Engine initialization complete. \n')

      

    
    def change_world(self, player, world):
        "переметить объект из одного мира в другой"
        prev_world = player.world
        new_world = self.worlds[world]
        player.location.pop_player(player.name)
        
        teleport_point = choice(new_world.teleports)
        new_position = new_world.choice_position(player, 5, teleport_point)
        li, lj = (new_position/TILESIZE/LOCATIONSIZE).get()
        
        

        new_location = new_world.locations[li][lj]
        new_location.add_player(player)

        self.players[player.name].world = new_world.name
        
        player.world = proxy(new_world)
        
        player.location = proxy(new_location)
        player.set_position(new_position)
        player.move_vector = Point()
        
        
        player.world_changed = True
        player.cord_changed = True
        #обновляем хэш объекта
        player.regid()
        
    
    def get_active_locations(self):
        "список активных локаций"
        return sum([world.active_locations.values() for world in self.worlds.values()], [])
    

        

        
    

            


game = __GameSingleton()


