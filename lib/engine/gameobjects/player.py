#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.enginelib.meta import *
from engine.mathlib import chance
from engine.enginelib.units_lib import Unit, Striker, Stats
from engine.gameobjects.shells import Ball
from engine.enginelib.movable import Movable
from engine.enginelib.skills import Skill
from engine.enginelib.equipment import Equipment
from engine.enginelib.map_observer import MapObserver

import  share.game_protocol as protocol

class Player(Respawnable, Unit, MapObserver, Striker, Guided, Stats, Skill, Equipment, HierarchySubject):
    "класс игрока"
    min_dist = 10
    prev_looked = set()
    speed = TILESIZE*0.5
    hp = 10 #60
    BLOCKTILES = ['stone', 'forest', 'ocean', 'lava']
    SLOWTILES = {'water':0.5, 'bush':0.3}
    damage = 5
    default_skills = 10
    fraction='players'

    def __init__(self, name, look_size=PLAYER_LOOK_RADIUS):
        GameObject.__init__(self, name)
        Unit.mixin(self, self.speed, self.hp, 'players')
        
        HierarchySubject.mixin(self)
        
        MapObserver.mixin(self, look_size)
        Striker.mixin(self,2, self.damage)
        Respawnable.mixin(self, 10, 30)
        Stats.mixin(self)
        Skill.mixin(self,self.default_skills)
        Equipment.mixin(self)

        self.set_shell(Ball)


        self.change_objects = False
        self.__actions__ = {'ApplyItem': self.ApplyItem, 'Move' : self.Move,
                            'Strike' : self.Strike, 'Skill' : self.Skill}
    
    def accept_response(self):
        data = self.location.name, self.location.size, self.position, self.location.background
        yield protocol.Newlocation(*data)
        
    def handle_response(self):
        #если попал в новый мир
        #cdef set new_looked, observed, old_players
        #cdef dict events
        #cdef list new_players
        if self.cord_changed or self.location_changed or self.respawned:
            self.observe()
        
        if self.location_changed or self.respawned:
            new_trig = True
            if self.location_changed:
                yield protocol.Newlocation(self.location.name, self.location.size, self.position, self.location.background)
                self.location_changed = False

            elif self.respawned:
                yield protocol.Respawn(self.position)
                self.respawned = False

        else:
            new_trig = False
            
        if self.position_changed:
            yield protocol.MoveCamera(self.move_vector)
    
        #если изменилась клетка - смотрим новые тайлы и список тайлов в радусе обзора

        if self.cord_changed or new_trig:
            new_looked, observed = self.look_map()
            yield protocol.LookLand(new_looked, observed)

        
        if self.chunk.check_players() or new_trig:
            new_players, events, old_players = self.look_objects()
            if new_players or events or old_players:
                yield protocol.LookObjects(new_players, events, old_players)





        #если изменились собственные статы
        if self.stats_changed:
            yield protocol.PlayerStats(*Stats.get_stats(self))
        
        #если изменился список игроков лнлайн
        if self.location.game.guided_changed:
            yield protocol.PlayersList(self.location.game.get_guided_list(self.name))
            
        #если изменилис предметы
        if self.equipment_changed:
            yield protocol.EquipmentDict(self.look_items())
            self.equipment_changed = False
            
    def Strike(self, vector):
        self.strike_ball(vector)
    
    def Move(self, vector, destination):
            Movable.move(self, vector, destination)
    
    def Look(self):
        return MapObserver.look(self)
    
    def Skill(self):
        self.skill()
    
    def ApplyItem(self, slot):
        self.apply_item(slot)
    
    def get_args(self):
        return Breakable.get_args(self)

    def handle_respawn(self):
        MapObserver.handle_respawn(self)
        Breakable.handle_respawn(self)
    
    def update(self):
        #print 'update player'
        Movable.update(self)
        Striker.update(self)
        Breakable.update(self)
        Stats.update(self)
        DiplomacySubject.update(self)
    
    def complete_round(self):
        #print 'complete_round player'
        Movable.complete_round(self)

    def __del__(self):
        HierarchySubject.__del__(self)
        Equipment.__del__(self)
        Unit.__del__(self)

    
