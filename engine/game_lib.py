#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.mathlib import *

from collections import defaultdict

Eventlist = lambda: defaultdict(set)

class Event:
    def __init__(self, name, object_type, position, action, args, timeout=0):
        self.name = name
        self.object_type = object_type
        self.position = position
        self.action = action
        self.args = tuple(args)
        self.timeout = timeout
    
    def get_tuple(self):
        return self.name, self.object_type, self.position.get(), self.action, self.args
    
    def alive(self):
        if self.timeout:
            self.timeout-=1
            return True
        else:
            return False
    
    def __hash__(self):
        try:
            return hash((self.name, self.object_type, self.position, self.action, self.args))
        except:
             print self.name, self.object_type, self.position, self.action, self.args
        
class ObjectContainer(object):
    def __init__(self, players = {},solid_objects = {},guided_players={},
                 static_objects = defaultdict(dict),events = Eventlist(),
                 static_events = Eventlist()):
        self.players = players

        self.solid_objects = solid_objects #твердые объект, способные сталкиваться
        self.guided_players = guided_players #управляемые игроки
        self.static_objects = static_objects #неподвижные объекты
        
        self.events = events #события объекто
        self.static_events = static_events #события статических объектов
    
    def __add__(self, cotainer):
        if isinstance(container, ObjectContainer):
            players = self.players + container.players
            solid_o = self.solid_objects + container.solid_objects
            guided_p = self.guided_players + container.guided_players
            static_o = self.static_objects + container.static_objects
            events = self.events + container.events
            static_e = self.static_events + container.static_events
            new_container = ObjectContainer(players,solid_o,guided_p,static_o,events,static_e)
            return new_container
    
    def clear_events(self):
        "очищает события в конце раунда"
        new_events = Eventlist()
        for cord, eventlist in self.events.items():
            for event in eventlist:
                if event.alive():
                    new_events[cord].add(event)
        self.events = new_events
        self.static_events.clear()
    
    
