#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.mathlib import Point, NullPoint
from game_objects import *

from worldmaps.mapgen import load_map

from weakref import proxy

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
            monster = object_type(self.mapname, position)

class MetaWorld(MetaWorldTools):
    "базовый класс карты"
    monster_count = 0
    def __init__(self, game, name, mapname):
        self.game = game
        self.name = name
        self.mapname = mapname
        
        self.map, self.size, self.background = load_map(mapname)
        
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
        while 1:
            
            position = start +Point(randrange(-radius, radius), randrange(-radius, radius))
            i,j = position.get()
            if 0<i<self.size and 0<j<self.size:
                if not self.map[i][j] in player.BLOCKTILES:
                    position = position*TILESIZE
                    return position
    
    

class World(MetaWorld):
    "поверхность"
    def __init__(self, name, game):
        MetaWorld.__init__(self, game, name, 'ground')
    
    def start(self):
        self.create_item(100, Cave)
        self.create_object(200, Zombie)
        self.create_object(50, Lych)
        self.create_object(50, Ghast)
        self.create_object(50, Cat)
    
    
    
    
class UnderWorld(MetaWorld):
    "подземелье"
    def __init__(self, name,  game):
        MetaWorld.__init__(self, game, name,  'underground')
    
    def start(self):
        self.create_item(200, Stair)
        self.create_object(100, Zombie)
        self.create_object(20, Lych)
        self.create_object(20, Ghast)
        self.create_object(20, Cat)



########################################################################

#список инкременаторов к индексу на соседние локации
near_cords = [cord.get() for cord in (Point(-1,1),Point(0,1),Point(1,1),
                                    Point(-1,0),             Point(1,0),
                                    Point(-1,-1),Point(0,-1),Point(1,-1))]

class LocationActivity:
    "функционал локации для работы с ее активностью"
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
    "функционал локации для работы с событиями"
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
        self.events = [event for event in self.timeouted_events if event.update()]
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
    "функционал локации для работы с объектами"
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
            self.add_solid(player)
   
    
    def pop_player(self, name):
        "удаляет ссылку из списка игроков"
        if name in self.players:
            self.new_players = True
            
            player = self.players[name]
            
            if isinstance(player, engine_lib.ActiveState):
                self.unset_primary_activity()
            
            if name in self.solids:
                self.remove_solid(name)
            
            del self.players[player.name]
        
        
    def check_players(self):
        "проверяет изменился ли список объекто в локации и соседних локациях"
        if self.new_players:
            return True
        for location in self.nears:
            if location.new_players:
                return True
        return False
    
    
    def get_players_list(self):
        "выдает список всех игроков в локации и соседних локациях"
        players = sum([(location.players.values()) for location in self.nears], self.players.values())
        
        return players

    def clear_players(self):
        "удаляет игроков отмеченных для удаления в списке remove_list"
        if self.remove_list:
            remove_list = self.remove_list.copy()
            self.remove_list.clear()
            
            for name, force in remove_list.items():
                self.remove_player(name, force)
    
    def remove_player(self, name, force = False):
        "удаляет игрока, если его метод remove возвращает true"
        player = self.players[name]
        result = player.remove()
        if result or force:
            position = player.position
            if player.delayed:
                player.add_event('delay', ())
                
            if name in self.remove_list:
                self.remove_list.remove(name)
            
            if name in self.solids:
                self.remove_solid(name)
                
            if isinstance(player, engine_lib.ActiveState):
                self.unset_primary_activity()
            
            self.new_players = True
            del self.players[name]
            self.world.game.remove_player_from_list(name)
        else:
            player.handle_remove()
    
    def add_to_remove(self, name, force):
        "добавляе игрок в список на удаление"
        self.remove_list[name] = force

    
    #статические объекты

    def add_static_object(self, player):
        "добавляет ссылку на статический объект"
        self.static_objects[player.name] = player
        if isinstance(player, engine_lib.ActiveState):
            self.set_primary_activity()
        if isinstance(player, engine_lib.Solid):
            self.add_solid(player)
        self.new_static_objects = True

    
    def pop_static_object(self, name):
        "удаляет ссылку из списка сатических объектов"
        player = self.static_objects[name]
        
        if isinstance(player, engine_lib.ActiveState):
            self.unset_primary_activity()
        
        if name in self.solids:
            self.remove_solid(name)
        
        self.new_static_objects = True
        del self.static_objects[player.name]
        

    
    def get_static_objects_list(self):
        "возвращает список статических объекто в в локации и соседних локациях"
        start = self.static_objects.values()
        static_objects = sum([location.static_objects.values() for location in self.nears], start)
        
        return static_objects
    

    
    
    
    def check_static_objects(self):
        "проверяет изменился ли список сттических объектов в локации и соседних локациях"
        if self.new_static_objects:
            return True
        for location in self.nears:
            if location.new_static_objects:
                return True
        return False
    
    
    
    def clear_static_objects(self):
        "удаляет статические оъекты добавленные для удаления"
        if self.remove_static_list:
            remove_list = self.remove_static_list.copy()
            self.remove_static_list.clear()
    
            for name, force in remove_list.items():
                self.remove_static_object(name, force)
        

    
    def remove_static_object(self, name, force = False):
        "удаляет статические объекты, если метод remove вернул False то откладывет удаление объекта"
        result = self.static_objects[name].remove()
        if result or force:
            
            player = self.static_objects[name]
            position = player.position
            if player.delayed:
                player.add_event('delay', ())
            
            if name in self.solids:
                self.remove_solid(name)
            
            if isinstance(player, engine_lib.ActiveState):
                self.unset_primary_activity()
    
            
            self.new_static_objects = True
            del self.static_objects[name]
            self.world.game.remove_static_object_from_list(name)
  
    

    
    def add_to_remove_static(self, name, force):
        "добавляет статический объект в список для удаления"
        self.remove_static_list[name] = force
    
    #
    def add_solid(self, solid):
        self.solids[solid.name] = solid
    
    def remove_solid(self, name):
        del self.solids[name]
    
    def get_solids_list(self):
        "выдает ссылку на твердый объект в локации и соседних локациях"        
        solids = sum([location.solids.values() for location in self.nears], self.solids.values())
        return solids
    

    
    
    def update(self):
        "очистка объекьтов"
        self.clear_players()
        self.clear_static_objects()
    
    def complete_round(self):
        "вызывается при завершении раунда, удаляет списки для удаления и обнуляет триггеры новых объектов"
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

