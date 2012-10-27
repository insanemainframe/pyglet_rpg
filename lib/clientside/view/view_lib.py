#!/usr/bin/env python
# -*- coding: utf-8 -*-
from types import ClassType            
from clientside.client_objects import all

class ViewTools:
    "создает словарь из классов клиентских объектов"
    def __init__(self, window, surface):
        self.surface = surface
        self.window = window
        
        self.module = all
        self.module.Meta.init_cls(surface)
        self.object_dict = {}
        self.objects = {}
        self.deleted_objects = []
        
        self.eventnames = []
        self.timeout_events = []

        self.focus_object = False
        
        for name in dir(self.module):
            Class = getattr(self.module, name)
            if type(Class) is ClassType:
                if issubclass(Class, self.module.Meta):
                    self.object_dict[name] = Class
    
    def insert_events(self, new_events={}):
        events = []
        for gid, eventlist in new_events.items():
            for action, args, timeout in eventlist:
                if gid in self.objects:
                    events.append((gid, action, args))
                    self.eventnames.append(gid)
                    if timeout>0:
                        self.timeout_events.append((gid, timeout, action, args))
                    print action, args
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
        game_object = self.object_dict[str(object_type)](name, position, **args)
        game_object.gid = gid
        
        self.objects[gid] = game_object
        if object_type=='Self':
            self.focus_object = gid
        #print 'create_object', gid, name
    
    def remove_object(self, gid):
        #print 'remove_object', gid, self.objects[gid].name
        if self.objects[gid].gid == self.focus_object :
                self.focus_object = False
        del self.objects[gid]
    
    def clear(self):
        self.objects = {}

