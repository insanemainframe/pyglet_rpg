#!/usr/bin/env python
# -*- coding: utf-8 -*-
#разделяемое состояние всех объектов игры
from config import *


from weakref import proxy, ProxyType
from random import  choice
from collections import OrderedDict, Sequence

import gc
gc.enable()

from sys import getrefcount

from share.point import Point

from engine.enginelib.meta import Guided, HierarchySubject, Container, Respawnable
from engine.enginelib.movable import Movable
from engine.world.location import Metalocation


        
class __GameSingleton(object):
    "синглтон игрового движка - хранит карты, все объекты, и предоставляет доступ к ним"
    def __init__(self):
        self.guided_players = {} #управляемые игроки
        self.players = {}
        
        self.monster_count = 0
        self.guided_changed = False
        self.stopped = False

    
    def start(self):
        print('Engine initialization...')
        self_proxy = proxy(self)
        
        self.locations = {}
        self.active_locations = {}
        
        self.locations['ground'] = Metalocation(self_proxy, 'ground')
        self.locations['underground'] = Metalocation(self_proxy, 'underground')
        self.locations['underground2'] = Metalocation(self_proxy, 'underground2')
        self.mainlocation = self.locations['ground']
        
        for location in self.locations.values():
            print('location %s initialization' % location.name)
            location.start()
            location.save(True)

        
        
        print('Engine initialization complete. \n')

    def add_active_location(self, location):
        self.active_locations[location.name] = location

    def remove_active_location(self,location):
        key = location.name
        if key in self.active_locations:
            del self.active_locations[key]
    
        
    def _new_object(self, player):
        "создает динамический объект"
        assert not isinstance(player, ProxyType)

        if isinstance(player, Guided):  print ('game._new_object', player)
        
        self.players[player.name] = player
         
        if isinstance(player, Guided):
            self.guided_players[player.name] = proxy(player)
                

        
    
    
    def _remove_object(self, player, force = False):
        assert player.name in self.players
        name = player.name

        result = player.handle_remove()
        if  force:
            result = 'disconnect', ()

        if force or not isinstance(player, Respawnable):
            assert result is True or isinstance(result, Sequence) and len(result)>1

            if isinstance(player, Guided):  print ('game._remove_object', player, force)

            if result is True:
                player.location.pop_object(player)
            else:
                player.location.pop_object(player, result)

            if isinstance(player, Guided):
                print ("%s refcount: %s" % (player, getrefcount(self.players[name])))

            del self.players[name]
            
        else:
            player.location.pop_object(player)

            player._REMOVE = False
            player.regid()
            player.respawned = True
            
            if isinstance(player, Movable):
                player.flush()

            chunk_cord = game.mainlocation.main_chunk.cord
            self.mainlocation.add_object(player, chunk_cord)

            player.handle_respawn()


            
            
            
    


    def remove_guided(self, name):
        print ('\n\n remove_guided', name)
        assert name in self.guided_players

        player = self.guided_players[name]

        self._remove_object(player, True)
        del self.guided_players[name]

    


    def change_location(self, player, location_name, new_position = None):
        "переметить объект из одного мира в другой"

        assert isinstance(player, ProxyType)
        assert new_position is None or isinstance(new_position, Point)

        if isinstance(player, Guided):  print ('game.change_location', player, location_name
        )
        prev_location = player.location

        new_location = self.locations[location_name]
    

        #нходим новый чанк
        dest_chunk_cord = choice(new_location.teleports)
        print (dest_chunk_cord)
        
        if not new_position:
            (chunk_i, chunk_j),new_position = new_location.choice_position(player, chunk=dest_chunk_cord)
            new_chunk_cord = Point(chunk_i, chunk_j)
        else:
            new_chunk_cord = new_location.get_chunk_cord(new_position)
        
        #меняем локацию
        prev_location.pop_object(player)
        new_location.add_object(player, new_chunk_cord, new_position)
        new_chunk = player.chunk
                
        
        
        if isinstance(player, Movable):
            player.flush()
        #обновляем хэш объекта
        player.regid()
        
        if isinstance(player, HierarchySubject):
            for slave in player.get_slaves():
                (chunk_i, chunk_j), position = new_location.choice_position(slave, dest_chunk_cord)
                self.change_location(slave, new_location.name, new_position = position)
        
    
    def get_active_chunks(self):
        "список активных локаций"
        for_sum = [list(loc.get_active_chunks()) for loc in self.active_locations.values() if loc.has_active_chunks()]
        return sum(for_sum, [])
    
    def get_guided_list(self, self_name):
        return [player.get_online_tuple(self_name) for player in self.guided_players.values()]
    
    def save(self):
        for location in self.locations.values():
            location.save()

    def stop(self):
        self.stopped = True

    def debug(self):
        for location in self.locations.values():
            location.debug()

        if DEBUG_REFS:
            for player in self.players.values():
                count = getrefcount(player)
                if hasattr(player, '_max_count'):
                    max_count = player._max_count
                else:
                    max_count = 4
                if count>max_count:
                    print ('\n',player.name, count)
                    raw_input('Debug:')
                    player._max_count = count



game = __GameSingleton()

