#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.mathlib import *

class Event:
    def __init__(self, name, object_type, position, action, args, timeout=0):
        hash(args)
        self.name = name
        self.object_type = object_type
        self.position = position
        self.cord = position/TILESIZE
        self.action = action
        self.args = tuple(args)
        self.timeouted = timeout
    
    def get_tuple(self):
        return self.name, self.object_type, self.position.get(), self.timeouted, self.action, self.args
    
    def update(self):
        self.timeouted-=1
        return bool(self.timeouted)
    
    def __hash__(self):
        return hash((self.name, self.action, self.args))
    
    def __eq__(self, another):
        return another.__hash__()==self.__hash__()
    
    def __ne__(self, another):
        return another.__hash__()!=self.__hash__()
        
    
    def __str__(self):
        return "Event: %s %s %s <%s>" % (self.object_type,self.name, self.position, self.action) 

