#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from clientside.gui.gui_lib import Drawable
from clientside.gui.window import create_tile, GuiElement, LEFT_BUTTON, RIGHT_BUTTON
from clientside.view.view_lib import ViewTools
from clientside.client_objects import static_objects
from share.mathlib import *

class StaticObjectView(Drawable, ViewTools, GuiElement):
    def __init__(self, window, surface):
        Drawable.__init__(self)
        ViewTools.__init__(self, window, surface, static_objects)
        GuiElement.__init__(self, surface)
        self.prev_hovered = False
        
        

    
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

    def find_object(self, x,y):
        m_position =  Point(x,y) - self.surface.center
        m_position = self.surface.position +m_position

        for gid, game_object in self.objects.items():
            dist = abs(game_object.position - m_position)
            #print game_object.position
            if dist <= TILESIZE:
                return game_object, gid
    
    def on_mouse_motion(self, x, y, dx, dy):
        result = self.find_object(x,y)
        if result:
            hovered, gid = result
            if not self.prev_hovered==gid:
                hovered.hover()
                if self.prev_hovered:
                    if self.prev_hovered in self.objects:
                        self.objects[self.prev_hovered].unhover()
                        self.prev_hovered = False
                
            self.prev_hovered = gid
        else:
            if self.prev_hovered:
                if self.prev_hovered in self.objects:
                    self.objects[self.prev_hovered].unhover()
                    self.prev_hovered = False

    
    def on_mouse_press(self, x, y, button, modifiers):
        "перехватывавем нажатие левой кнопки мышки"
        #левая кнопка - движение
        if self.window.objects.focus_object:
            focus = self.window.objects.focus_object
            focus_position = self.window.objects.objects[focus].position
        else:
            focus_position = self.surface.position

        if button==LEFT_BUTTON:
            result = self.find_object(x,y)
            if result:
                hovered, gid = result
 
                self.surface.vector = hovered.position - focus_position
                self.destination = hovered.name
            else:
                self.surface.vector = Point(x,y) - (self.surface.center - (self.surface.position - focus_position))

            return True
        return False
            
            
        
    
    
        
        
        
