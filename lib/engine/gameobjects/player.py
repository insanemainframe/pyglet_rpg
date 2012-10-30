#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.enginelib.meta import *
from engine.mathlib import chance
from engine.enginelib.units_lib import *
from engine.gameobjects.shells import Ball
from engine.enginelib.movable import Movable
from engine.enginelib.skills import *
from engine.enginelib.map_observer import MapObserver
from engine.enginelib import wrappers

import  share.game_protocol as protocol

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

    def __init__(self, name, player_position, look_size=PLAYER_LOOK_RADIUS):
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
        
    def handle_response(self):
        #если попал в новый мир
        if self.cord_changed or self.world_changed or self.respawned:
            self.observe()
        
        if self.world_changed or self.respawned:
            new_trig = True
            if self.world_changed:
                yield protocol.NewWorld(self.world.name, self.world.size, self.position, self.world.background)
                self.world_changed = False

            elif self.respawned:
                yield protocol.Respawn(self.position)
                self.respawned = False

        else:
            new_trig = False
            
        if self.position_changed:
            yield protocol.MoveCamera(self.move_vector)
    
        #если изменилась клетка - смотрим новые тайлы и список тайлов в радусе обзора
        objects_trig = self.location.check_players()
        events_trig = self.location.check_events()

        

        if self.cord_changed or objects_trig or events_trig or new_trig:
            look_result = self.look_map(for_objects = events_trig, for_events = events_trig, force = new_trig)

            (new_looked, observed), (players, events)  = look_result

            yield protocol.LookLand(new_looked, observed)

            if players:
                yield protocol.LookObjects(players)
            if events:
                yield protocol.LookEvents(events)



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
            
    @wrappers.alive_only()
    def Strike(self, vector):
        self.strike_ball(vector)
    
    @wrappers.alive_only()
    def Move(self, vector, destination):
            Movable.move(self, vector, destination)
    
    def Look(self):
        return MapObserver.look(self)
    
    def Skill(self):
        self.skill()
    
    def ApplyItem(self, slot):
        self.apply_item(slot)
    
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
    
    @classmethod
    def choice_position(cls, world, location, i ,j):
        for tile in world.get_near_tiles(i,j):
            if tile in cls.BLOCKTILES:
                return False

        for ij in world.get_near_cords(i,j) + [(i,j)]:
                for player in world.tiles[Point(*ij)]:
                    if isinstance(player, Solid):
                        return False

        for player in location.get_players_list():
            if isinstance(player, DiplomacySubject):
                if player.fraction=='monsters':
                    dist = abs(Point(i,j)*TILESIZE - player.position)
                    if dist<=cls.min_dist*TILESIZE:
                        return False
                    
        


        

        return True
