#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from weakref import proxy

from share.point import Point
from engine.enginelib.meta import DynamicObject, StaticObject, ActiveState, Solid


#список инкременаторов к индексу на соседние локации
near_cords = [cord.get() for cord in (Point(-1,1),Point(0,1),Point(1,1),
                                    Point(-1,0),             Point(1,0),
                                    Point(-1,-1),Point(0,-1),Point(1,-1))]

 

class LocationEvents:
    "функционал локации для работы с событиями"
    def __init__(self):
        self.new_events = False
    
    def set_event(self):
        self.new_events = True
        
    
    def check_events(self):
        if self.new_events:
            return True
        for location in self.nears:
            if location.new_events:
                return True
        
        return False
    
    def clear_events(self):
        self.new_events = False
        
    
    
    def complete_round(self):
        self.clear_events()
    





class LocationObjects:
    "функционал локации для работы с объектами"
    def __init__(self):
        self.players = {}
        
        self.solids = {}
        
        self.new_players = False
        
        self.remove_list = {}
        
    
    def add_object(self, player):
        "добавляет ссылку на игрока"
        if isinstance(player, ActiveState):
            self.set_primary_activity()

        if isinstance(player, Solid):
            self.add_solid(player)

        self.new_players = True
        self.players[player.name] = proxy(player)


        
    
    def pop_object(self, player):
        "удаляет ссылку из списка игроков"
        name = player.name
        if name in self.players:
            player = self.players[name]
            del self.players[player.name]
            self.new_players = True


            if isinstance(player, ActiveState):
                    self.unset_primary_activity()
                
            if isinstance(player, Solid):
                self.remove_solid(name)

            if name in self.remove_list:
                del self.remove_list[name]


    def remove_object(self, player, force = False):
        "удаляет игрока, если его метод remove возвращает true"
        name = player.name
        del self.players[name]


        result = player.remove()
        if result or force:
            position = player.position
            if player.delayed:
                player.add_event('delay', ())
                
            
            
            if name in self.solids:
                self.remove_solid(name)
                
            if isinstance(player, ActiveState):
                self.unset_primary_activity()
            
            self.new_players = True
            
            self.world.game.remove_object(player)

            if name in self.remove_list:
                del self.remove_list[name]

        else:
            player.handle_remove()
        
        
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
            for name, force in self.remove_list.items():
                player = self.players[name]
                self.remove_object(player, force)

            self.remove_list.clear()
    
    

    

    


        


  
    
    def add_to_remove(self, player, force):
        "добавляет статический объект в список для удаления"
        name = player.name
        self.remove_list[name] = force
    
    #
    def add_solid(self, solid):
        self.solids[solid.name] = proxy(solid)
    
    def remove_solid(self, name):
        del self.solids[name]
    
    def get_solids_list(self):
        "выдает ссылку на твердый объект в локации и соседних локациях"        
        solids = sum([location.solids.values() for location in self.nears], self.solids.values())
        return solids
    

    
    def update(self):
        "очистка объекьтов"
        self.clear_players()
    
    def complete_round(self):
        "вызывается при завершении раунда, удаляет списки для удаления и обнуляет триггеры новых объектов"
        self.remove_list.clear()
        
        self.new_players = False

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
        self.world.active_locations[self.cord.get()] = self
    
    def unset_activity(self):
        key = self.cord.get()
        if key in self.world.active_locations:
            del self.world.active_locations[key]
        else:
            print('key error', key)



class Location(LocationActivity, LocationEvents, LocationObjects):
    "небольшие локаци на карте, содержат ссылки на соседние локации и хранят ссылки на объекты и события"
    def __init__(self, world, i,j):
        self.world = world
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
                self.nears.append(near_location)
        
    
    def update(self):
        LocationObjects.update(self)
    
    def complete_round(self):
        LocationObjects.complete_round(self)
        LocationEvents.complete_round(self)



