#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from clientside.gui.gui_lib import Drawable
from clientside.gui.window import create_tile
from clientside.view.view_lib import ViewTools
from clientside.view import static_objects
from share.mathlib import *

class StaticObjectView(Drawable, ViewTools):
    def __init__(self, surface):
        Drawable.__init__(self)
        ViewTools.__init__(self, surface, static_objects)
    

        
    
    
    def round_update(self):
        for name in self.deleted_objects:
            if not self.objects[name].delayed:
                self.remove_object(name)
            else:
                if name not in self.eventnames:
                    self.remove_object(name)
        
        self.eventnames = []
        self.deleted_objects = []
        
        new_events = [(gid, object_type, position, timeout-1, action, args)
        for gid, object_type, position, timeout, action, args in self.timeout_events]
        self.timeout_events = []
        if new_events:
            self.insert_events(new_events)
        
            
    
    def update(self):
        self.shift = self.surface.position - self.surface.center
        self.tiles = []
        for object_name, game_object in self.objects.items():
            tiles = game_object.draw()
            self.tiles.extend(tiles)
        
