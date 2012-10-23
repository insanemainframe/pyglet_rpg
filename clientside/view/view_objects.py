#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from config import *

from clientside.gui.gui_lib import Drawable
from clientside.client_objects import dynamic_objects
from clientside.view.view_lib import ViewTools

from share.mathlib import *


from collections import defaultdict

class ObjectsView(Drawable, ViewTools):
    "отображение объектов"
    def __init__(self, window, surface):
        Drawable.__init__(self)
        ViewTools.__init__(self, window, surface, dynamic_objects)
        self.focus_object = False

        
        
    def antilag(self, shift):
        if self.focus_object:
            self.objects[self.focus_object].vector+=shift
    
                

    def update(self, delta):
        #обновляем объекты
        [game_object.update(delta) for game_object in self.objects.values()]
        
        
        #отображение объектов
        self.tiles = []
        self.shift = self.surface.position - self.surface.center
        for object_name, game_object in self.objects.items():
            self.tiles.extend(game_object.draw())
    
    def remove_timeouted(self):
        remove_list = set()
        for name, game_object in self.objects.items():
            if game_object.delayed and (name not in self.events):
                remove_list.add(name)
        
        [self.remove_object(name) for name in remove_list]
        
    
    def clear(self):
        #удаляем объекты с меткой
        remove_list = []
        for name, game_object in self.objects.items():
            if game_object.REMOVE:
                remove_list.append(name)
        
        for name in remove_list:
            self.remove_object(name)
    
    def filter(self):
        #удаляем объекты для которых больше нет на карте
        for gid in self.deleted_objects:
            if gid in self.objects:
                if not self.objects[gid].delayed:
                    self.remove_object(gid)
                else:
                    if gid not in self.eventnames:
                        self.remove_object(gid)
                    
        for gid, gameobject in self.objects.items():
            if gameobject.delayed:
                if gid not in self.eventnames:
                    self.remove_object(gid)
        
        self.eventnames = []
        self.deleted_objects = []
    
    def round_update(self):
        [game_object.round_update() for game_object in self.objects.values()]
        
        new_events = [(gid, object_type, position, timeout-1, action, args)
        for gid, object_type, position, timeout, action, args in self.timeout_events]
        self.timeout_events = []
        if new_events:
            self.insert_events(new_events)
        
    def force_complete(self):
        [game_object.force_complete() for game_object in self.objects.values()]
    
    
        
            
    

