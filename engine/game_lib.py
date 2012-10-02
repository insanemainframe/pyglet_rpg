#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.mathlib import *
from engine_lib import StaticObject

from weakref import proxy
from collections import defaultdict


class Event:
    def __init__(self, event_id, name, object_type, position, action, args, timeout=0):
        self.event_id = event_id
        self.position = position
        self.name = name
        self.object_type = object_type
       
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
        return hash(self.event_id)
    
    def __eq__(self, event):
        return self.event_id==event.event_id
   


dictadd = lambda d1, d2: dict(d1.items() +d2.items())

class ObjectContainer(object):
    "контейнер содержащий объекты и события"
    def __init__(self):
        self.players ={}

        self.solid_objects = {}#твердые объект, способные сталкиваться
        self.guided_players = {} #управляемые игроки
        self.static_objects = defaultdict(dict) #неподвижные объекты
        
        self.events = set() #события объекто
        self.static_events = set() #события статических объектов
        
        self.timeout_events = set()
    
    def __add__(self, container):
        new_container = ObjectContainer()
        
        new_container.players.update(self.players)
        new_container.players.update(container.players)
        
        new_container.solid_objects.update(self.solid_objects)
        new_container.solid_objects.update(container.solid_objects)
        
        new_container.guided_players.update(self.guided_players)
        new_container.guided_players.update(container.guided_players)
        
        new_container.static_objects.update(self.static_objects)
        new_container.static_objects.update(container.static_objects)

        new_container.events = set(tuple(self.events) + tuple(container.events))
        new_container.static_events = set(tuple(self.static_events) + tuple(container.static_events))
        new_container.timeout_events = set(tuple(self.timeout_events) + tuple(container.timeout_events))
        
        return new_container
    
    
    def add_event(self, event):
        
        self.events.add(event)
                
    def add_static_event(self, event):
        self.static_events.add(event)
    
    def clear_events(self):
        "очищает события в конце раунда"
        self.events = set() #[event for event in self.timeout_events if event.alive()])
        
        self.static_events.clear()

