#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.mathlib import Point, NullPoint
from mapgen import load_map

from weakref import proxy


class World:
    "класс карты как со стороны ссервера"
    def __init__(self, game):
        self.game = game
        
        self.map, self.size = load_map()
        self.location_size = self.size/LOCATIONSIZE
        print 'creting world size',self.size
        
        self.locations = []
        self.active_locations = {}
        
        self.create_locations()
        self.create_links()
    
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
    
    def get_loc_cord(self, position):
        return (position/TILESIZE/LOCATIONSIZE).get()
    

near_cords = [cord.get() for cord in (Point(-1,1),Point(0,1),Point(1,1),
                                    Point(-1,0),             Point(1,0),
                                    Point(-1,-1),Point(0,-1),Point(1,-1))]

class LocationActivity:
    def __init__(self):
        self.primary_activity = 0
        self.slavery_activity = 0
    

    def unset_primary_activity(self):
        self.primary_activity-=1
        if self.primary_activity<=0:
            [location.unset_slavery_activity() for location in self.nears]
            if self.slavery_activity==0:
                self.unset_activity()
    
    def set_primary_activity(self):
        self.primary_activity+=1
        if self.primary_activity==1:
            [location.set_slavery_activity() for location in self.nears]
            
            if self.slavery_activity<=0:
                self.set_activity()
        

    def unset_slavery_activity(self):
        self.slavery_activity -= 1
        
        if self.primary_activity<=0 and self.slavery_activity==0:
            self.unset_activity()
    
    def set_slavery_activity(self):
        self.slavery_activity += 1
        
        if self.primary_activity<=0 and self.slavery_activity==1:
            self.set_activity()
    
    
    def set_activity(self):
        self.world.active_locations[self.cord.get()] = proxy(self)
    
    def unset_activity(self):
        key = self.cord.get()
        if key in self.world.active_locations:
            del self.world.active_locations[key]
        else:
            print 'key error', key
    

 

class LocationEvents:
    def __init__(self):
        self.events = []
        self.static_events = []
        
        self.new_events = False
        self.new_static_events = False
        
        self.timeouted_events = []
        self.timeouted_static_events = []
    
    def add_event(self,event):
        self.events.append(event)
        
        if event.timeouted:
            self.timeouted_events.append(event)
    
    def get_events(self):
        events = sum([location.events for location in self.nears], self.events)
        return events
    
    def check_events(self):
        if self.events:
            return True
        for location in self.nears:
            if location.events:
                return True
        
        return False
    
    def clear_events(self):
        self.events = []
        #self.events = [event for event in self.timeouted_events if event.update()]
        if self.events:
            self.new_events = True
        else:
            self.new_events = False
        
    
    def add_static_event(self, event):
        self.static_events.append(event)
        
        if event.timeouted:
            self.timeouted_static_events.append(event)
    
    def get_static_events(self):
        static_events = sum([location.static_events for location in self.nears], self.static_events)
        return static_events
    
    def check_static_events(self):
        if self.static_events:
            return True
        for location in self.nears:
            if len(location.static_events):
                return True
        return False
    
    def clear_static_events(self):
        self.static_events = [event for event in self.timeouted_static_events if event.update()]
        if self.static_events:
            self.new_static_events = True
        else:
            self.new_static_events = False
    
    def complete_round(self):
        self.clear_events()
        self.clear_static_events()
    





class LocationObjects:
    def __init__(self):
        self.players = {}
        self.static_objects = {}
        
        self.solids = {}
        
        self.new_players = False
        self.new_static_objects = False
        
        self.remove_list = {}
        self.remove_static_list = {}
        
    
    def add_player(self, player):
        "добавляет ссылку на игрока"
        self.new_players = True
        self.players[player.name] = player
        
        if isinstance(player, engine_lib.ActiveState):
            self.set_primary_activity()
        
        if isinstance(player, engine_lib.Solid):
            self.solids[player.name] = player
   
    
    def pop_player(self, name):
        self.new_players = True
        
        player = self.players[name]
        
        if isinstance(player, engine_lib.ActiveState):
            self.unset_primary_activity()
        
        if isinstance(player, engine_lib.Solid):
            del self.solids[player.name]
        
        del self.players[player.name]
        

    
    def get_players_list(self):
        players = sum([(location.players.values()) for location in self.nears], self.players.values())
        
        return players


    def add_static_object(self, player):
        self.static_objects[player.name] = player
        if isinstance(player, engine_lib.ActiveState):
            self.set_primary_activity()
        if isinstance(player, engine_lib.Solid):
            self.solids[player.name] = player
        self.new_static_objects = True

    
    def pop_static_object(self, name):
        player = self.static_objects[name]
        
        if isinstance(player, engine_lib.ActiveState):
            self.unset_primary_activity()
        
        if isinstance(player, engine_lib.Solid):
            del self.solids[player.name]
        
        self.new_static_objects = True
        del self.static_objects[player.name]
        

    
    def get_static_objects_list(self):
        start = self.static_objects.values()
        static_objects = sum([location.static_objects.values() for location in self.nears], start)
        
        return static_objects
    
    
    def get_solids_list(self):
        solids = sum([location.solids.values() for location in self.nears], self.solids.values())
        return solids

    
    def check_players(self):
        for location in self.nears:
            if location.new_players:
                return True
        return False
    
    def check_static_objects(self):
        for location in self.nears:
            if location.new_static_objects:
                return True
        return False
    
    def clear_players(self):
        remove_list = self.remove_list.copy()
        self.remove_list.clear()
        
        for name, force in remove_list.items():
            self.remove_player(name, force)
    
    def clear_static_objects(self):
        remove_list = self.remove_static_list.copy()
        self.remove_static_list.clear()

        for name, force in remove_list.items():
            self.remove_static_object(name, force)
        
        
    
    def remove_player(self, name, force = False):
        player = self.players[name]
        result = player.remove()
        if result or force:
            print 'remove', name
            position = player.position
            if player.delayed:
                player.add_event('delay', ())
                
            if name in self.remove_list:
                self.remove_list.remove(name) 
            if name in self.solids:
                del self.solids[name]
            if isinstance(player, engine_lib.ActiveState):
                self.unset_primary_activity()
            
            self.new_players = True
            del self.players[name]
            self.world.game.remove_player_from_list(name)
        else:
            player.handle_remove()
            
        
        

    
    def remove_static_object(self, name, force = False):
        "удаляет статические объекты, если метод remove вернул False то откладывет удаление объекта"
        result = self.static_objects[name].remove()
        if result or force:
            
            player = self.static_objects[name]
            position = player.position
            if player.delayed:
                player.add_event('delay', ())
            
            if name in self.solids:
                del self.solids[name]
            
            if isinstance(player, engine_lib.ActiveState):
                self.unset_primary_activity()
            
            self.new_static_objects = True
            del self.static_objects[name]
            self.world.game.remove_static_object_from_list(name)
  
    
    def add_to_remove(self, name, force):
        self.remove_list[name] = force
    
    def add_to_remove_static(self, name, force):
        self.remove_static_list[name] = force

    def update(self):
        self.clear_players()
        self.clear_static_objects()
    
    def complete_round(self):
        self.remove_list.clear()
        self.remove_static_list.clear()
        
        self.new_players = False
        self.new_static_objects = False

class Location(LocationActivity, LocationEvents, LocationObjects):
    "небольшие локаци на карте, содержат ссылки на соседние локации и хранят ссылки на объекты и события"
    def __init__(self, world, i,j):
        self.world = proxy(world)
        self.i, self.j = i,j
        self.cord = Point(i,j)
        
        LocationActivity.__init__(self)
        LocationObjects.__init__(self)
        LocationEvents.__init__(self)
        
        self.nears = []
        
    def create_links(self):
        "создает сслыки на соседние локации"
        for i,j in near_cords:
            try:
                near_location = self.world.locations[self.i+i][self.j+j]
            except IndexError:
                pass
            else:
                self.nears.append(proxy(near_location))
        
    
    def update(self):
        LocationObjects.update(self)
    
    def complete_round(self):
        LocationObjects.complete_round(self)
        LocationEvents.complete_round(self)
        
def init():
    from game import game
    global game
    import engine_lib
    global engine_lib

