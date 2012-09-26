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
from mapgen import load_map

from engine_lib import Solid, Guided

class World:
    "класс карты как со стороны ссервера"
    def __init__(self):
        World.map, World.size = load_map()
        print 'server world size',World.size


players = {}
solid_objects = {}
guided_players = {}

world = World()
size = world.size
    
updates = defaultdict(list)
update_counter = 0
ball_counter = 0


class UnknownAction(Exception):
    pass


def add_event(name, position, altposition, action, args=[]):
    global update_counter
    if action:
        uid = update_counter
        update_counter += 1
        map_position = (position/TILESIZE).get()
        object_type = players[name].__class__.__name__
        
        update = (uid, (name, object_type, position, action, args))
            
        updates[map_position].append(update)
        
        if altposition:
            alt_key = (altposition/TILESIZE).get()
            updates[alt_key].append(update)

def new_object(player):
    "ововестить всех о новом объекте"
    players[player.name] = player
    #
    if isinstance(player, Guided):
        guided_players[player.name] = proxy(player)
    if isinstance(player, Solid):
        solid_objects[player.name] = proxy(player)
    #добавляем обновление
    key = (player.position/TILESIZE).get()
    add_event(player.name, player.position, False, 'exist', [NullPoint.get()])

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
            if hasattr(players[name], 'REMOVE'):
                if players[name].REMOVE:
                    remove_list.append(name)
        #
        for name in remove_list:
            remove_object(name)

def remove_object(name, force = False):
    print 'remove', name, force
    result = players[name].remove()
    if result or force:
        player = players[name]
        if isinstance(player, Guided):
            del guided_players[name]
        if isinstance(player, Solid):
            del solid_objects[name]
        del players[name]
    else:
        players[name].REMOVE = False
