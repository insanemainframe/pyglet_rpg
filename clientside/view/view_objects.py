#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from config import *

from clientside.gui.gui_lib import GameWindow, Drawable
from clientside.view import client_objects
from clientside.view.view_lib import ViewTools

from share.mathlib import *


from collections import defaultdict

class ObjectsView(GameWindow, Drawable, ViewTools):
    "отображение объектов"
    def __init__(self):
        Drawable.__init__(self)
        ViewTools.__init__(self, client_objects)
        self.objects = {}
        self.tiles = []
        self.events = defaultdict(list)
        self.focus_object = False
        
    def antilag(self, shift):
        if self.focus_object:
            self.events[self.focus_object]+=shift
    
    def insert(self, events=[]):
        self.events.clear()
        if events:
            for name, object_type, position, action, args, delayed in events:
                if action=='create':
                    self.create_object(name, object_type, position, delayed)
                elif action=='remove':
                    self.remove_object(name)
                elif action=='delay':
                    print 'delay', name
                    if not name in self.objects:
                        self.create_object(name, object_type, position, delayed)
                    self.objects[name].delayed = True
                else:
                    if name in name in self.objects:
                        self.events[name].append((position, object_type, action, args, delayed))
                        
                    else:
                        self.events[name].append((position, object_type, action, args, delayed))
                        self.create_object(name, object_type, position, delayed)
                        if args=='self':
                            self.focus_object = name          
        
        #удаяем объекты с мтеокй REMOVE
        [self.remove_object(name) for name in self.objects.keys() if self.objects[name].REMOVE]
        
        if self.events:
            for object_name, events_list in self.events.items():
                for position, object_type, action ,args, timeouted in events_list:
                    if not object_name in self.objects:
                        self.create_object(object_name, object_type, position, timeouted)
                    if not self.objects[object_name].REMOVE:
                        self.objects[object_name].handle_action(action, args)
                    else:
                        self.remove_object(object_name)
                

    def update(self, delta):
        #обновляем объекты
        [game_object.update(delta) for game_object in self.objects.values()]
        
        #отображение объектов
        self.tiles = []
        self.shift = self.position - self.center
        for object_name, game_object in self.objects.items():
            self.tiles.extend(game_object.draw())
    
    def remove_timeouted(self):
        remove_list = set()
        for name, game_object in self.objects.items():
            if game_object.delayed and name not in self.events:
                remove_list.add(name)
        
        [self.remove_object(name) for name in remove_list]
        
    def filter(self, observed):
        new_objects = {}
        for object_name, game_object in self.objects.items():
            cord = (game_object.position/TILESIZE).get()
            if cord in observed and not game_object.REMOVE:
                new_objects[object_name] = game_object
        
        self.objects = new_objects
    
    def round_update(self):
        [client_objects.ClientObject.round_update(game_object) for game_object in self.objects.values()]
        
    def force_complete(self):
        [game_object.force_complete() for game_object in self.objects.values()]
        
            
    
    def clear(self):
        self.events.clear()
        #self.objects.clear()
    
    def remove_object(self, name):
        if name in self.events:
            del self.events[name]
        if name in self.objects:
            del self.objects[name]
