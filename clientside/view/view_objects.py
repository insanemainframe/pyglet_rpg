#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from config import *

from clientside.gui.gui_lib import Drawable
from clientside.view import client_objects
from clientside.view.view_lib import ViewTools

from share.mathlib import *


from collections import defaultdict

class ObjectsView(Drawable, ViewTools):
    "отображение объектов"
    def __init__(self, surface):
        Drawable.__init__(self)
        ViewTools.__init__(self, surface, client_objects)
        self.focus_object = False
        self.eventnames = []
        
    def antilag(self, shift):
        if self.focus_object:
            self.objects[self.focus_object].vector+=shift
    
    def insert_objects(self, looked_objects):
        looked_keys = set( looked_objects.keys())
        client_keys = set(self.objects.keys())
        
        new_objects = looked_keys - client_keys
        self.deleted_objects = client_keys - looked_keys
        
        for gid in new_objects:
            name, object_type, position, args = looked_objects[gid]
            self.create_object(gid, name, object_type, position, args)
            if object_type=='Self':
                self.focus_object = gid
            
        
        
    def insert_events(self, new_events=[]):
        events = []
        for name, object_type, position, action, args in new_events:
                if name in name in self.objects:
                    events.append((name, object_type, position, action, args))
                    self.eventnames.append(name)
                        

        
        for object_name, object_type, position, action, args in events:
            self.objects[object_name].handle_action(action, args)
        
        #удаяем объекты с мтеокй REMOVE

                

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
        for name in self.deleted_objects:
            if not self.objects[name].delayed:
                self.remove_object(name)
            else:
                if name not in self.eventnames:
                    self.remove_object(name)
                    
        for name, gameobject in self.objects.items():
            if gameobject.delayed:
                if name not in self.eventnames:
                    self.remove_object(name)
        
        self.eventnames = []
        self.deleted_objects = []
    
    def round_update(self):
        [game_object.round_update() for game_object in self.objects.values()]
        
    def force_complete(self):
        [game_object.force_complete() for game_object in self.objects.values()]
    
    
        
            
    

