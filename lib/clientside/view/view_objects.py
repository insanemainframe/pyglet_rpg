#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from config import *

from clientside.client_objects import all as object_types
from clientside.gui.window import create_tile, GuiElement, LEFT_BUTTON, RIGHT_BUTTON
from clientside.gui.gui_lib import Drawable

from share.point import *

from types import ClassType            
from collections import defaultdict

class ObjectsView(Drawable, GuiElement):
    "отображение объектов"
    def __init__(self, window, surface):
        Drawable.__init__(self)
        GuiElement.__init__(self, surface)
        self.surface = surface
        self.window = window
        
        object_types.Meta.init_cls(surface)
        
        self.objects = {}
        self.delayed_objects = []
        

        self.focus_object = False

        self.object_dict = {}

        for name in dir(object_types):
            Class = getattr(object_types, name)
            if type(Class) is ClassType:
                if issubclass(Class, object_types.Meta):
                    self.object_dict[name] = Class

        self.prev_hovered = False
        self.focus_object = False

    def insert_events(self, new_events={}):
        for gid, eventlist in new_events.items():
            for action, args in eventlist:
                if gid in self.objects:

                    self.objects[gid].handle_action(action, args)
                else:
                    print '%s not in objects: action %s' % (gid, action)
        
            
    
    def insert_objects(self, new_players, old_players):
        for gid, name, object_type, position, args in new_players:
            self.create_object(gid, name, object_type, position, args)


        for gid, delay_arg in old_players:
            self.remove_object(gid, delay_arg)
            
        
            
    def create_object(self, gid, name, object_type, position, args={}):
        game_object = self.object_dict[str(object_type)](name, position, **args)
        game_object.gid = gid
        
        self.objects[gid] = game_object
        if object_type=='Self':
            self.focus_object = gid
        #print 'create_object', gid, name
    
    def remove_object(self, gid, delay_arg = False):
        #print 'remove_object', gid, self.objects[gid].name
        if self.objects[gid].gid == self.focus_object :
                self.focus_object = False
        if delay_arg:
            action, args = delay_arg
            print 'dealyarg', args
            
            self.objects[gid].handle_action(action, args)
            self.delayed_objects.append(gid)
        else:
            del self.objects[gid]
    
    def clear(self):
        self.objects = {}

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
    

        
    
    def clear(self):
        #удаляем объекты с меткой
        delayed_objects = self.delayed_objects[:]
        for gid in self.delayed_objects:
            if gid in self.objects:
                if self.objects[gid]._REMOVE:
                    self.remove_object(gid)
                    self.delayed_objects.remove(gid)


    
    def round_update(self):
        [game_object.round_update() for game_object in self.objects.values()]
        

        
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
            
            
    
    
        
            
    

