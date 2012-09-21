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
update_counter = 0
ball_counter = 0


class UnknownAction(Exception):
    pass


def add_update(name, position, altposition, action, args=[]):
    global update_counter
    if action:
        uid = update_counter
        update_counter += 1
        map_position = (position/TILESIZE).get()
        object_type = players[name].object_type
        
        update = (uid, (name, object_type, position, action, args))
            
        updates[map_position].append(update)
        
        if altposition:
            alt_key = (altposition/TILESIZE).get()
            updates[alt_key].append(update)

def new_object(player):
    "ововестить всех о новом объекте"
    players[player.name] = player
    #добавляем обновление
    key = (player.position/TILESIZE).get()
    add_update(player.name, player.position, False, 'move', [NullPoint.get()])

def choice_position(ObjectClass):
    while 1:
        start = size/2 - 7
        end = size/2 + 7
        position = Point(randrange(start, end), randrange(start, end))
        i,j = position.get()
        if not world.map[i][j] in ObjectClass.BLOCKTILES:
            position = position*TILESIZE
            return position

def detect_collisions():
        "определяем коллизии"
        for Name, Player in players.items():
            for name, player in players.items():
                if name!=Name:
                    distance = abs(Player.position - player.position)
                    if distance <= Player.radius+player.radius:
                        if Player.mortal and player.human and player.name!=Player.striker:
                            player.alive = False
                            Player.REMOVE = True
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

def remove_object(name):
    player = players[name]
    player.die()
    add_update(player.name, player.prev_position, NullPoint, 'remove')
    del players[name]
