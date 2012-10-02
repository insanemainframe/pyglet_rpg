#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.mathlib import *

from collections import defaultdict

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

Eventlist = lambda arg = {}: defaultdict(set, arg)

class ObjectContainer(object):
    def __init__(self):
        self.players = {}

        self.solid_objects = {} #твердые объект, способные сталкиваться
        self.guided_players = {} #управляемые игроки
        self.static_objects = defaultdict(dict) #неподвижные объекты
        
        self.events = Eventlist() #события объекто
        self.static_events = Eventlist() #события статических объектов
        
        self.timeout_events = Eventlist()
        self.timeout_static_events = Eventlist()
    
    
    def clear_events(self):
        "очищает события в конце раунда"
        self.events = Eventlist({cord:set([event for event in eventlist if event.alive()])
                        for cord, eventlist in self.timeout_events.items()})
        
        self.static_events.clear()
    
    
