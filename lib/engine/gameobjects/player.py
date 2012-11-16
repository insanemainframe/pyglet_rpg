#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.enginelib.meta import *
from engine.mathlib import chance
from engine.enginelib.units_lib import Unit, Striker, Stats
from engine.gameobjects.shells import Ball
from engine.enginelib.mutable import MutableObject
from engine.enginelib.skills import Skill
from engine.enginelib.equipment import Equipment
from engine.enginelib.map_observer import MapObserver

from  share.gameprotocol.server_responses import *

class Player(Respawnable, Unit, MapObserver, Striker, Guided, Stats, Skill, Equipment, HierarchySubject):
    "класс игрока"
    min_dist = 10
    prev_looked = set()
    speed = TILESIZE*0.5
    player_hp = 100 #60
    BLOCKTILES = ['stone', 'forest', 'ocean', 'lava']
    SLOWTILES = {'water':0.5, 'bush':0.3}
    damage = 20
    strike_speed = 2
    default_skills = 1000

    fraction='players'

    def __init__(self, name, look_size=PLAYER_LOOK_RADIUS):
        Unit.__init__(self, name, self.player_hp, self.speed, 'players')
        
        
        HierarchySubject.mixin(self)
        
        MapObserver.mixin(self, look_size)
        Striker.mixin(self,self.strike_speed, self.damage)
        Respawnable.mixin(self, 10, 30)
        Stats.mixin(self)
        Skill.mixin(self,self.default_skills)
        Equipment.mixin(self)

        self.set_strike_speed(5)
        self.set_shell(Ball)


        self.__actions__ = {'ApplyItem': self.ApplyItem, 'Move' : self.Move,
                            'Strike' : self.Strike, 'Skill' : self.Skill}
    
    def accept_response(self):
        data = self.location.name, self.location.size, self.position, self.location.background
        yield NewLocation(*data)
        
    def handle_response(self):
        #если попал в новый мир
        #cdef set new_looked, observed, old_players
        #cdef dict events
        #cdef list new_players
        #if self.cord_changed or self.location_changed or self.respawned:
        self.observe()
        
        if self.location_changed or self.respawned:
            new_trig = True
            if self.location_changed:
                yield NewLocation(self.location.name, self.location.size, self.position, self.location.background)
                self.location_changed = False

            elif self.respawned:
                yield Respawn(self.position)
                self.respawned = False

        else:
            new_trig = False
            
        if self.position_changed:
            yield MoveCamera(self.get_move_vector())
    
        #если изменилась клетка - смотрим новые тайлы и список тайлов в радусе обзора

        if self.cord_changed or new_trig:
            new_looked, observed = self.look_map()
            yield LookLand(new_looked, observed)

        chunk = self.chunk
        
        #if new_trig or self.has_events or chunk.check_events() or chunk.check_players():
        new_players, events, old_players = self.look_objects()
        yield LookObjects(new_players, events, old_players)





        #если изменились собственные статы
        if self.is_stats_changed():
            yield PlayerStats(*Stats.get_stats(self))
        
        #если изменился список игроков лнлайн
        if self.is_guided_changed():
            yield PlayersList(self.get_online_list())
            
        #если изменилис предметы
        if self.is_equipment_changed():
            yield EquipmentDict(self.look_items())
            
            
    def Strike(self, vector):
        vector = Position(*vector.get())
        self.strike_ball(vector)
    
    def Move(self, vector, destination):
        vector = Position(*vector.get())
        MutableObject.move(self, vector, destination)
    
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
        Breakable.update(self)
        DiplomacySubject.update(self)
    


    def __del__(self):
        HierarchySubject.__del__(self)
        Equipment.__del__(self)
        Unit.__del__(self)

    
