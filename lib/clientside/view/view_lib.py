#!/usr/bin/env python
# -*- coding: utf-8 -*-
from types import ClassType            
from collections import defaultdict
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
        self.delayed_objects = []
        
        self.eventnames = []
        self.timeout_events = defaultdict(list)

        self.focus_object = False
        
        for name in dir(self.module):
            Class = getattr(self.module, name)
            if type(Class) is ClassType:
                if issubclass(Class, self.module.Meta):
                    self.object_dict[name] = Class
    
    def insert_events(self, new_events={}):
        for gid, eventlist in new_events.items():
            for action, args, timeout in eventlist:
                if timeout>0 or gid in self.objects:
                    self.eventnames.append(gid)
                    timeout-=1
                    if timeout>0:
                        self.timeout_events[gid].append((action, args, timeout))
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
            action = delay_arg[0]
            args = delay_arg[1:]
            self.objects[gid].handle_action(action, args)
            self.delayed_objects.append(gid)
        else:
            del self.objects[gid]
    
    def clear(self):
        self.objects = {}

