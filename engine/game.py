#!/usr/bin/env python
# -*- coding: utf-8 -*-
#разделяемое состояние всех объектов игры
from collections import defaultdict
from random import randrange
from weakref import proxy
from sys import path
path.append('../')

from config import *

from share.mathlib import Point, NullPoint
from maplib import World

from engine_lib import Solid, Guided



class UnknownAction(Exception):
    pass

players = {}

solid_objects = {}
guided_players = {}

events = defaultdict(list)
event_counter = 0
ball_counter = 0

world = World()
size = world.size


def add_event(name, position, altposition, action, args=[]):
    global event_counter
    if action:
        uid = event_counter
        event_counter += 1
        map_position = (position/TILESIZE).get()
        object_type = players[name].__class__.__name__
        
        event = (uid, (name, object_type, position, action, args))
            
        events[map_position].append(event)
        
        if altposition:
            alt_key = (altposition/TILESIZE).get()
            events[alt_key].append(event)

def new_object(player):
    "ововестить всех о новом объекте"
    players[player.name] = player
    #
    new_object_proxy(player)
    #добавляем обновление
    key = (player.position/TILESIZE).get()
    add_event(player.name, player.position, False, 'exist', [NullPoint.get()])


def new_object_proxy(player):
    if isinstance(player, Guided):
        guided_players[player.name] = proxy(player)
    if isinstance(player, Solid):
        solid_objects[player.name] = proxy(player)

def remove_object_proxy(player):
    name = player.name
    if isinstance(player, Guided):
            del guided_players[name]
    if isinstance(player, Solid):
        del solid_objects[name]
    
def choice_position(player, radius=7, start=False):
    if not start:
        start = Point(size/2,size/2)
    else:
        start = start/TILESIZE
    while 1:
        
        position = start +Point(randrange(-radius, radius), randrange(-radius, radius))
        i,j = position.get()
        if not world.map[i][j] in player.BLOCKTILES:
            position = position*TILESIZE
            return position
    
def clear():
        "удаляем объекты отмеченыне меткой REMOVE"
        remove_list = []
        for name in players:
            if players[name].REMOVE:
                remove_list.append(name)
        #
        for name in remove_list:
            remove_object(name)

def clear_events():
    events.clear()

def remove_object(name, force = False):
    result = players[name].remove()
    if result or force:
        player = players[name]
        remove_object_proxy(player)
        del players[name]
    else:
        players[name].REMOVE = False

