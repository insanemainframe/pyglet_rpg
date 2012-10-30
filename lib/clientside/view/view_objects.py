#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from config import *

from clientside.gui.window import create_tile, GuiElement, LEFT_BUTTON, RIGHT_BUTTON
from clientside.gui.gui_lib import Drawable
from clientside.view.view_lib import ViewTools

from share.point import *


from collections import defaultdict

class ObjectsView(Drawable, ViewTools, GuiElement):
    "отображение объектов"
    def __init__(self, window, surface):
        Drawable.__init__(self)
        ViewTools.__init__(self, window, surface)
        GuiElement.__init__(self, surface)
        self.prev_hovered = False
        self.focus_object = False

    def get_focus_position(self):
        if self.focus_object:
            obj = self.objects[self.focus_object]
            return obj.position
        else:
            return False

        
        
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
        
        if self.timeout_events:
            self.insert_events(self.timeout_events)
        self.timeout_events.clear()
        
    def force_complete(self):
        [game_object.force_complete() for game_object in self.objects.values()]


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
            
            
    
    
        
            
    

