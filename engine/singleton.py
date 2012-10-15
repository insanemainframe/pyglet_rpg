#!/usr/bin/env python
# -*- coding: utf-8 -*-
#разделяемое состояние всех объектов игры
from config import *

from random import randrange, choice
from weakref import proxy


from share.mathlib import Point
from engine.singleton_lib import ObjectContainer, ObjectItem
from engine import gameworlds


        
class __GameSingleton(ObjectContainer):
    "синглтон игрового движка - хранит карты, все объекты, и предоставляет доступ к ним"
    def __init__(self):
        ObjectContainer.__init__(self)
        self.guided_changed = False

    
    def start(self):
        print('Engine initialization...')
        
        self.worlds = {}
        self.worlds['ground'] = gameworlds.World('ground',proxy(self))
        self.worlds['underground'] = gameworlds.UnderWorld('underground', proxy(self))
        self.worlds['underground2'] = gameworlds.UnderWorld2('underground2', proxy(self))
        
        self.mainworld = self.worlds['ground']
        
        for world in self.worlds.values():
            print('world %s initialization' % world.name)
            world.start()
        
        print('Engine initialization complete. \n')

      

    
    def change_world(self, player, world, new_position = False):
        "переметить объект из одного мира в другой"
        prev_world = player.world
        new_world = self.worlds[world]
        player.location.pop_player(player.name)
        
        teleport_point = choice(new_world.teleports)
        if not new_position:
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
        
        for related in player.related_objects:
            position = new_world.choice_position(related, 3, new_position)
            self.change_world(related, world, position)
        
    
    def get_active_locations(self):
        "список активных локаций"
        return sum([world.active_locations.values() for world in self.worlds.values()], [])
    
    def get_guided_list(self, self_name):
        f = lambda cont:  ('(%s)'% player.name if player.name==self_name else player.name, player.kills)
        return [f(player) for player in self.guided_players.values()]
    


game = __GameSingleton()


