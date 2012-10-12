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
import  share.game_protocol as protocol

class Player(Respawnable, Unit, MapObserver, Striker, Guided, Stats, Skill, DynamicObject):
    "класс игрока"
    prev_looked = set()
    speed = 30
    hp = 40
    BLOCKTILES = ['stone', 'forest', 'ocean', 'lava']
    SLOWTILES = {'water':0.5, 'bush':0.3}
    damage = 2

    def __init__(self, name, world, player_position, look_size):
        DynamicObject.__init__(self, name, world, player_position)
        Unit.__init__(self, self.speed, self.hp, Corpse, self.name)
        MapObserver.__init__(self, look_size)
        Striker.__init__(self,2, Ball, self.damage)
        Respawnable.__init__(self, 10, 30)
        Stats.__init__(self)
        Skill.__init__(self,10)
        self.change_objects = False
    
    def accept_response(self):
        data = self.world.name, self.world.size, self.position, self.world.background
        yield protocol.NewWorld(*data)
        yield protocol.LookEvents(self.look_events())
        
    def handle_response(self):
        if self.world_changed:
            yield protocol.NewWorld(self.world.name, self.world.size, self.position, self.world.background)
            yield protocol.LookLand(*self.look_map())
            yield protocol.LookPlayers(self.look_players(True))
            yield protocol.LookStaticObjects(self.look_static_objects(True))
            self.world_changed = False
            
    
        elif self.respawned:
            yield protocol.Respawn(self.position)
            yield protocol.LookLand(*self.look_map())
            yield protocol.LookPlayers(self.look_players(True))
            yield protocol.LookStaticObjects(self.look_static_objects(True))
            self.respawned = False
 
        
        else:
            if self.position_changed and not (self.respawned or self.world_changed):
                yield protocol.MoveCamera(self.move_vector)
        
            #если изменилась клетка - смотрим новые тайлы и список тайлов в радусе обзора
            if self.cord_changed:
                new_looked, observed = self.look_map()
                yield protocol.LookLand(new_looked, observed)
            
            #если изменилась клетка или изменились объекты в локации
            #смотрим список видимых объектов
            if self.cord_changed or self.location.check_players():
                players = self.look_players()
                if players:
                    yield protocol.LookPlayers(players)
            
            #если изменилась клетка или изменились статические объекты в локации
            #смотрим список видимых статических объектов
            if self.cord_changed or self.location.check_static_objects():
                static_objects = self.look_static_objects()
                if static_objects:
                    yield  protocol.LookStaticObjects(static_objects)
            
            #если есть новые события в локации
            if self.location.check_events():
                events = self.look_events()
                if events:
                    yield protocol.LookEvents(events)
            
            #если есть новй события статическиъ объекктов
            if self.location.check_static_events():
                yield protocol.LookStaticEvents(self.look_static_events(self))
            
            #если изменились собственные статы
            if self.stats_changed:
                yield protocol.PlayerStats(*Stats.get_stats(self))
            
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
    
    def get_args(self):
        return Deadly.get_args(self)
    
    @wrappers.alive_only(Deadly)
    def update(self):
        Movable.update(self)
        Striker.update(self)
        Deadly.update(self)
        Stats.update(self)
        DiplomacySubject.update(self)
    
    def complete_round(self):
        Movable.complete_round(self)
