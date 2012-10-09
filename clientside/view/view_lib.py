#!/usr/bin/env python
# -*- coding: utf-8 -*-
from types import ClassType            

class ViewTools:
    "создает словарь из классов клиентских объектов"
    def __init__(self, surface, module):
        self.surface = surface
        
        self.module = module
        self.module.Meta.init_cls(surface)
        self.object_dict = {}
        self.objects = {}
        self.deleted_objects = []
        for name in dir(self.module):
            Class = getattr(self.module, name)
            if type(Class) is ClassType:
                if issubclass(Class, self.module.Meta):
                    self.object_dict[name] = Class
            
    def create_object(self, gid, name, object_type, position, args={}):
        game_object = self.object_dict[object_type](name, position, **args)
        
        self.objects[gid] = game_object
    
    def remove_object(self, gid):
        del self.objects[gid]
    
    def clear(self):
        self.objects = {}

