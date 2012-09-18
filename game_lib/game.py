#!/usr/bin/env python
# -*- coding: utf-8 -*-
#разделяемое состояние всех объектов игры
from collections import defaultdict
from random import randrange

from sys import path
path.append('../')

from config import *

from math_lib import Point, NullPoint
from mapgen import load_map

class World:
    "класс карты как со стороны ссервера"
    def __init__(self):
        World.map, World.size = load_map()
        print 'server world size',World.size


players = {}
world = World()
size = world.size
    
updates = defaultdict(list)
ball_counter = 0


class UnknownAction(Exception):
    pass


def add_update(name, position, vector, action, *args):
    uid = hash((name, position, vector, action, args))
    map_position = (position/TILESIZE).get()
    if action=='move':
        tilename = args[0]
        update = (uid, (name, position, vector, 'move', tilename))
    elif action=='remove':
        update = (uid, (name, position, vector, 'remove', ()))
    else:
        raise UnknownAction(action)
        
    updates[map_position].append(update)
    
    if vector:
        alt_position = ((position+vector)/TILESIZE).get()
        updates[alt_position].append(update)

def new_object(player):
    "ововестить всех о новом объекте"
    players[player.name] = player
    #добавляем обновление
    key = (player.position/TILESIZE).get()
    update = (player.name, (player.position, player.move_vector, player.tilename))
    add_update(player.name, player.position, player.move_vector, 'move', player.tilename)

def choice_position():
    while 1:
        start = size/2 - 7
        end = size/2 + 7
        position = Point(randrange(start, end), randrange(start, end))
        i,j = position.get()
        if not world.map[i][j] in BLOCKTILES+TRANSTILES:
            position = position*TILESIZE
            return position
    
def remove_object(name):
    player = players[name]
    add_update(player.name, player.prev_position, NullPoint, 'remove')
    del players[name]
