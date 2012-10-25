#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.mathlib cimport Point

cdef class Event:
    def __init__(self, str name, str object_type, Point position, str action, args, timeout=0):
        self.name = name
        self.object_type = object_type
        self.position = position
        self.cord = position/TILESIZE
        self.action = action
        self.args = tuple(args)
        self.timeouted = int(timeout)
    
    def get_tuple(Event self):
        return self.name, self.object_type, self.position.get(), self.timeouted, self.action, self.args
    
    def update(Event self):
        self.timeouted-=1
        return bool(self.timeouted)

    def __richcmp__(Event self, Event event, int op):
        if op==2:
            return event.__hash__()==self.__hash__()
        elif op==3:
            return event.__hash__()!=self.__hash__()
    
    def __hash__(Event self):
        return hash((self.name, self.action, self.args))
   
    
    def __str__(Event self):
        return "Event: %s %s %s <%s>" % (self.object_type,self.name, self.position, self.action) 

