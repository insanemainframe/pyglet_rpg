#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.mathlib cimport Point

import  share.game_protocol as protocol


from engine.enginelib.meta import Respawnable, Guided,  DynamicObject, Solid, Deadly, DiplomacySubject
from engine.mathlib import chance
from engine.enginelib.units_lib import Unit, Stats, Striker
from engine.enginelib.movable import Movable 
from engine.enginelib.equipment import Equipment
from engine.enginelib.skills import Skill
from engine.enginelib.map_observer import MapObserver
from engine.enginelib import wrappers

from engine.gameobjects.shells import Ball
from engine.gameobjects.items import Corpse



class Player(Respawnable, Unit, MapObserver, Striker, Guided, Stats, Skill, Equipment, DynamicObject):
    "класс игрока"
    min_dist = 10
    prev_looked = set()
    speed = TILESIZE*0.5
    hp = 60
    BLOCKTILES = ['stone', 'forest', 'ocean', 'lava']
    SLOWTILES = {'water':0.5, 'bush':0.3}
    damage = 5
    default_skills = 10

    def __init__(self, name, Point player_position, look_size=LOOK_RADIUS):
        DynamicObject.__init__(self, name, player_position)
        Unit.__init__(self, self.speed, self.hp, Corpse, 'players')
        MapObserver.__init__(self, look_size)
        Striker.__init__(self,2, Ball, self.damage)
        Respawnable.__init__(self, 10, 30)
        Stats.__init__(self)
        Skill.__init__(self,self.default_skills)
        Equipment.__init__(self)
        self.change_objects = False
        self.__actions__ = {'ApplyItem': self.ApplyItem, 'Move' : self.Move,
                            'Strike' : self.Strike, 'Skill' : self.Skill}
    
    def accept_response(self):
        data = self.world.name, self.world.size, self.position, self.world.background
        yield protocol.NewWorld(*data)
        yield protocol.LookEvents(self.look_events())
        
    def handle_response(self):
        #если попал в новый мир
        if self.world_changed or self.respawned:
            if self.world_changed:
                yield protocol.NewWorld(self.world.name, self.world.size, self.position, self.world.background)
                self.world_changed = False

            elif self.respawned:
                yield protocol.Respawn(self.position)
                self.respawned = False

            yield protocol.MoveCamera(self.move_vector)
            yield protocol.LookLand(*self.look_map())
            yield protocol.LookPlayers(self.look_players(True))
            yield protocol.LookEvents(self.look_events())
            yield protocol.LookStaticObjects(self.look_static_objects(True))
            
            
        else:
            if self.position_changed:
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
            if self.has_events or self.location.check_events():
                events = self.look_events()
                yield protocol.LookEvents(events)
            
            #если есть новй события статическиъ объекктов
            if self.location.check_static_events():
                yield protocol.LookStaticEvents(self.look_static_events(self))
            
        #если изменились собственные статы
        if self.stats_changed:
            yield protocol.PlayerStats(*Stats.get_stats(self))
        
        #если изменился список игроков лнлайн
        if self.world.game.guided_changed:
            yield protocol.PlayersList(self.world.game.get_guided_list(self.name))
            
        #если изменилис предметы
        if self.equipment_changed:
            yield protocol.EquipmentDict(self.look_items())
            self.equipment_changed = False
            
    def Strike(self, Point vector):
        if self.alive:
            self.strike_ball(vector)
    
    def Move(self, Point vector, destination):
        if self.alive:
            Movable.move(self, vector, destination)
    
    def Look(self):
        return MapObserver.look(self)
    
    def Skill(self):
        if self.alive:
            self.skill()
    
    def ApplyItem(self, slot):
        if self.alive:
            self.apply_item(slot)
    
    def get_args(self):
        return Deadly.get_args(self)
    
    def update(self):
        if self.alive:
            Movable.update(self)
            Striker.update(self)
            Deadly.update(self)
            Stats.update(self)
            DiplomacySubject.update(self)
        else:
            Deadly.update(self)
    
    def complete_round(self):
        Movable.complete_round(self)
    
    @classmethod
    def choice_position(cls, world, location, i ,j):
        cdef int dist
        cdef str tile
        cdef list BLOCKTILES
        BLOCKTILES = cls.BLOCKTILES

        for player in location.get_players_list():
            if player.fraction=='monsters':
                dist = abs(Point(i,j)*TILESIZE - player.position)
                if dist<=cls.min_dist*TILESIZE:
                    return False
                    
        for tile in world.get_near_tiles(i,j):
            if tile in BLOCKTILES:
                return False


        for ij in world.get_near_cords(i,j) + [(i,j)]:
                for player in world.tiles[Point(*ij)]:
                    if isinstance(player, Solid):
                        return False

        return True
