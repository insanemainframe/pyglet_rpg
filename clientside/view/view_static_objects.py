#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from clientside.gui.gui_lib import Drawable
from clientside.gui.window import GameWindow

from clientside.view.view_lib import ViewTools
from clientside.view import static_objects
from share.mathlib import *

class StaticObjectView(GameWindow, Drawable, ViewTools):
    def __init__(self):
        Drawable.__init__(self)
        ViewTools.__init__(self, static_objects)
        self.eventnames = []
    
    def insert_objects(self, static_objects):
        looked_keys = set(static_objects.keys())
        client_keys = set(self.objects.keys())
        
        new_objects = looked_keys - client_keys
        self.deleted_objects = client_keys - looked_keys
        
        for name in new_objects:
            self.create_object(name, *static_objects[name])
        
        
    
    def insert_events(self,  events):
        for name, object_type, position, action, args, timeouted in events:
            if name in self.objects:
                self.objects[name].handle_action(action, args)
                self.eventnames.append(name)
    
    
    def round_update(self):
        for name in self.deleted_objects:
            if not self.objects[name].delayed:
                self.remove_object(name)
            else:
                if name not in self.eventnames:
                    self.remove_object(name)
        
        self.eventnames = []
        self.deleted_objects = []
        
            
    
    def update(self):
        self.shift = self.position - self.center
        self.tiles = []
        for object_name, game_object in self.objects.items():
            tiles = game_object.draw()
            self.tiles.extend(tiles)
        
