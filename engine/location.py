#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.mathlib import Point, NullPoint
from game_lib import ObjectContainer
from engine_lib import GameObject, Solid, Guided, StaticObject

from weakref import proxy

class Location(ObjectContainer):
    def __init__(self, cord):
        ObjectContainer.__init__(self)
        self.cord = cord
        self.i, self.j = cord.get()
    
    def add_object(self, player):
        if isinstance(player, GameObject):
            self.players[player.name] = proxy(player)
            self.new_object_proxy(player)
        else:
            raise TypeError()
    
    def new_object_proxy(self, player):
        "создает ссылки на объект в специальных списках объектов"
        name = player.name
        if isinstance(player, Guided):
            self.guided_players[name] = proxy(player)
        if isinstance(player, Solid):
            self.solid_objects[name] = proxy(player)
        if isinstance(player, StaticObject):
            cord = (player.position/TILESIZE).get()
            self.static_objects[cord][name] = proxy(player)
    
    def remove_object_proxy(self, name):
        "удаляет ссылки на объект из списков"
        player = self.players[name]
        if isinstance(player, Guided):
            del self.guided_players[name]
        if isinstance(player, Solid):
            del self.solid_objects[name]
        if isinstance(player, StaticObject):
            cord = (player.position/TILESIZE).get()
            del self.static_objects[cord][name]
        
    
    def remove_object(self, name):
        #print 'remove_object', self.cord, name
        self.remove_object_proxy(name)
        del self.players[name]

def init():
    from game import game
    global game
