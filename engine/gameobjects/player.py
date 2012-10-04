#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.engine_lib import *
from engine.mathlib import chance
from engine.gameobjects.units_lib import *
from engine.gameobjects.shells import Ball
from engine.gameobjects.movable import Movable
from engine.gameobjects.skills import *
from engine.gameobjects.map_observer import MapObserver


class Player(Respawnable, Unit, MapObserver, Striker, Guided, Stats, Skill, DynamicObject):
    "класс игрока"
    radius = TILESIZE/2
    prev_looked = set()
    speed = 40
    hp = 50
    BLOCKTILES = ['stone', 'forest', 'ocean']
    SLOWTILES = {'water':0.5, 'bush':0.3}
    damage = 2

    def __init__(self, name, player_position, look_size):
        DynamicObject.__init__(self, name, player_position)
        Unit.__init__(self, self.speed, self.hp, Corpse, self.name)
        MapObserver.__init__(self, look_size)
        Striker.__init__(self,2, Ball, self.damage)
        Respawnable.__init__(self, 10, 30)
        Stats.__init__(self)
        Skill.__init__(self,100)
    
    def accept(self):
        return [self.look_map(), self.look_events()]
        
    def handle_response(self):
        location = self.get_location()
        messages = []
        
        if not self.respawned:
            if self.position_changed:
                messages.append(self.camera_move())
        else:
            messages.append(Respawnable.handle_response(self))
            
        if self.cord_changed:
            messages.append(self.look_map())
    
        if location.check_events():
            messages.append(self.look_events())
        
        if location.check_static_events():
            messages.append(self.look_static_events())
        
        static_objects = self.look_static_objects()
        if static_objects:
            messages.append(static_objects)
        
        if self.stats_changed:
            messages.append(self.get_stats())
        

        return messages
 
    
    def camera_move(self):
        return ('MoveCamera', Movable.handle_request(self))
        
    def look_static_events(self):
        static_events = MapObserver.look_static_events(self)
        return ('LookStaticEvents', (static_events,))
    
    def look_static_objects(self):
        static_objects = MapObserver.look_static_objects(self)
        return ('LookStaticObjects', (static_objects, ))
    
    def look_events(self):
        events = MapObserver.look_events(self)
        return ('LookObjects', (events,))
    
    def look_map(self):
        new_looked, observed = MapObserver.look_map(self)
        return ('LookLand', (new_looked, observed))
    
    def get_stats(self):
        return ('PlayerStats', Stats.get_stats(self))
        
    @wrappers.action
    @wrappers.alive_only()
    def Strike(self, vector):
        self.strike_ball(vector)
    
    @wrappers.action
    @wrappers.alive_only()
    def Move(self, vector):
        Movable.move(self, vector)
    
    @wrappers.action
    def Look(self):
        return MapObserver.look(self)
    
    @wrappers.action
    def Skill(self):
        self.skill()
    

    
    @wrappers.alive_only(Deadly)
    def update(self):
        Movable.update(self)
        Striker.update(self)
        Deadly.update(self)
        Stats.update(self)
        DiplomacySubject.update(self)
    
    def complete_round(self):
        Movable.complete_round(self)
