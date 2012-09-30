#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.mathlib import *

from collections import defaultdict


class ObjectContainer(object):
    def __init__(self, players = {},solid_objects = {},guided_players={},
                 static_objects = defaultdict(dict),events = defaultdict(list),
                 static_events = defaultdict(list)):
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
