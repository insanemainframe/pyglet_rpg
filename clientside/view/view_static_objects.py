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
        self.objects = {}
        self.tiles = []
    
    def insert_objects(self, static_objects):
        if static_objects:
            for name, (object_type, position) in static_objects.items():
                self.create_object(name, object_type, position)
        
        
    
    def insert_events(self,  events):
        if events:
            for name, object_type, position, action, args, timeouted in events:
                if name in self.objects:
                    self.objects[name].handle_action(action, args)
    
    def filter(self, observed):
        new_objects = {}
        for object_name, game_object in self.objects.items():
            cord = (game_object.position/TILESIZE).get()
            if cord in observed and not game_object.REMOVE:
                new_objects[object_name] = game_object
        
        self.objects = new_objects
            
    
    def update(self):
        self.shift = self.position - self.center
        self.tiles = []
        for object_name, game_object in self.objects.items():
            tiles = game_object.draw()
            self.tiles.extend(tiles)
        
