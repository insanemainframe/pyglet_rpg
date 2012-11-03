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

from engine.enginelib.meta import Guided, HierarchySubject, Container
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
    
        
    def new_object(self, player):
        "создает динамический объект"
        assert not isinstance(player, ProxyType)
        self.players[player.name] = player
         
        if isinstance(player, Guided):
            self.guided_players[player.name] = proxy(player)
                

        
    
    
    def remove_object(self, player, force = False):
        name = player.name
        if name in self.players:
            if not force:
                result = player.handle_remove()
            else:
                result = 'disconnect', ()
            if result:
                assert result is True or isinstance(result, Sequence) and len(result)>1
                if result is True:
                    player.location.pop_object(player)
                else:
                    player.location.pop_object(player, result)
                del self.players[name]


            
            
            
        #print 'remove_object', name, name in self.players
    


    def remove_guided(self, name):
        player = self.guided_players[name]

        self.remove_object(player, True)

    


    def change_location(self, player, location_name, new_position = False):
        "переметить объект из одного мира в другой"
        ref_player = proxy(player)

        prev_location = player.location
        new_location = self.locations[location_name]
        
        prev_location.remove_object(player)
        player.chunk.pop_object(player)
        
        teleport_chunk = new_location.get_chunk(choice(new_location.teleports))
        
        if not new_position:
            new_position = new_location.choice_position(player, teleport_chunk)
        li, lj = (new_position/TILESIZE/CHUNK_SIZE).get()
        
        

        new_chunk = new_location.chunks[li][lj]
        new_chunk.add_object(ref_player)
        new_location.add_object(ref_player)

        
        player.location = proxy(new_location)
        
        
        player.chunk = proxy(new_chunk)
        player.set_position(new_position)
        player.flush()
        
        
        player.location_changed = True
        player.cord_changed = True
        if isinstance(player, Movable):
            player.flush()
        #обновляем хэш объекта
        player.regid()
        
        if isinstance(player, HierarchySubject):
            for slave in player.get_slaves():
                position = new_location.choice_position(slave, new_chunk)
                self.change_location(slave, new_location, position)
        
        if isinstance(player, Container):
            for related in player.related_objects:
                related.location = proxy(new_location)
                related.chunk = proxy(new_chunk)
    
    def get_active_chunks(self):
        "список активных локаций"
        for_sum = [location.get_active_chunks() for location in self.active_locations.values() if location.has_active_chunks()]
        return sum(for_sum, [])
    
    def get_guided_list(self, self_name):
        f = lambda cont:  ('(%s)'% player.name if player.name==self_name else player.name, player.kills)
        return [f(player) for player in self.guided_players.values()]
    
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
                    print '\n',player.name, count
                    #print 'refs:', gc.get_referrers(player)
                    raw_input('Debug:')
                    player._max_count = count



game = __GameSingleton()


