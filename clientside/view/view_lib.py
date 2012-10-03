#!/usr/bin/env python
# -*- coding: utf-8 -*-
from types import ClassType            

class ViewTools:
    "создает словарь из классов клиентских объектов"
    def __init__(self, module):
        self.module = module
        self.object_dict = {}
        for name in dir(self.module):
            Class = getattr(self.module, name)
            if type(Class) is ClassType:
                if issubclass(Class, self.module.Meta):
                    self.object_dict[name] = Class
            
    def create_object(self, name, object_type, position, timeouted=False):
        game_object = self.object_dict[object_type](name, position)
        game_object.timeouted = timeouted
        if timeouted:
            print name
        self.objects[name] = game_object
    
    def remove_object(self, name):
        print 'remove', name
        del self.objects[name]
    
    def clear_objects(self):
        "удаляет объекты вне поля зрения"
        pass
