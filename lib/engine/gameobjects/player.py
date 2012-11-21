#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from server_logger import debug

from engine.enginelib.meta import *
from engine.mathlib import chance
from engine.enginelib.units_lib import Unit, Striker, Stats
from engine.gameobjects.shells import Ball
from engine.gameobjects.items import Sceptre

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
    player_hp = 600
    BLOCKTILES = ['stone', 'forest', 'ocean', 'lava']
    SLOWTILES = {'water':0.5, 'bush':0.3}
    strike_speed = 2
    strike_impulse = 60
    default_skills = 1000

    fraction='players'

    def __init__(self, name, look_size=PLAYER_LOOK_RADIUS):
        Unit.__init__(self, name, self.player_hp, self.speed, 'players')
        
        
        HierarchySubject.mixin(self)
        
        MapObserver.mixin(self, look_size)
        Striker.mixin(self,self.strike_speed, self.strike_impulse)
        Respawnable.mixin(self, 10, 30)
        Stats.mixin(self)
        Skill.mixin(self,self.default_skills)
        Equipment.mixin(self)

        self.set_strike_speed(5)
        self.set_shell(Ball)
        
        self.add_related(Sceptre())


        self.set_actions(ApplyItem = self.ApplyItem, Move = self.Move,
                        Strike = self.Strike, Skill = self.Skill)
    
    def accept_response(self):
        data = self.location.name, self.location.size, self.position, self.location.background
        yield NewLocation(*data)
        
    def handle_response(self):
        chunk = self.chunk
        new_trig = self.location_changed or self.respawned

        if self.cord_changed:
            self.observe()

        
        if new_trig:
            if self.location_changed:
                yield NewLocation(self.location.name, self.location.size, self.position, self.location.background)
                self.location_changed = False

            elif self.respawned:
                yield Respawn(self.position)
                self.respawned = False


            
        if self.position_changed:
            yield MoveCamera(self.get_move_vector())
    
        #если изменилась клетка - смотрим новые тайлы и список тайлов в радусе обзора

        if self.cord_changed or new_trig:
            new_looked, observed = self.look_map()
            yield LookLand(new_looked, observed)

        
        if self.cord_changed or chunk.check_positions() or chunk.check_players()  or new_trig:
            new_players, old_players = self.look_objects()
            if new_players or old_players:
                yield LookObjects(new_players, old_players)

        if chunk.check_events():
            events = self.look_events()
            if events:
                yield LookEvents(events)





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
        if self.is_set_tool():
            self.use_tool()
        else:
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
        super(Player, self).handle_respawn()

    def handle_change_location(self):
        super(Player, self).handle_change_location()

 
    
    def __update__(self, cur_time):
        super(Player, self).__update__(cur_time)
    



    
