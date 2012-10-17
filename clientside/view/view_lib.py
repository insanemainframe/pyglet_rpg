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
        
        self.eventnames = []
        self.timeout_events = []
        
        for name in dir(self.module):
            Class = getattr(self.module, name)
            if type(Class) is ClassType:
                if issubclass(Class, self.module.Meta):
                    self.object_dict[name] = Class
    
    def insert_events(self, new_events=[]):
        events = []
        for gid, object_type, position, timeout, action, args in new_events:
                if gid in self.objects:
                    events.append((gid, object_type, position, action, args))
                    self.eventnames.append(gid)
                    if timeout>0:
                        self.timeout_events.append((gid, object_type, position, timeout, action, args))
        
        for gid, object_type, position, action, args in events:
            self.objects[gid].handle_action(action, args)
    
    def insert_objects(self, looked_objects):
        looked_keys = set( looked_objects.keys())
        client_keys = set(self.objects.keys())
        
        new_objects = looked_keys - client_keys
        self.deleted_objects = client_keys - looked_keys
        
        for gid in new_objects:
            name, object_type, position, args = looked_objects[gid]
            self.create_object(gid, name, object_type, position, args)
        
            
    def create_object(self, gid, name, object_type, position, args={}):
        game_object = self.object_dict[object_type](name, position, **args)
        
        self.objects[gid] = game_object
        if object_type=='Self':
                self.focus_object = gid
        #print 'create_object', gid, name
    
    def remove_object(self, gid):
        #print 'remove_object', gid, self.objects[gid].name
        if self.objects[gid].__class__.__name__=='Self':
                self.focus_object = False
        del self.objects[gid]
    
    def clear(self):
        self.objects = {}

