#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from share.errors import *
xrange = range

from engine.mathlib import Cord, Position, ChunkCord

from share.serialization import loads, dumps, load, dump

from engine.world.chunk import Chunk
from engine.world._location.map_source import load_map
from engine.enginelib.meta  import Savable, SavableRandom
from engine import game_objects

from random import randrange, choice
from weakref import proxy,ProxyType
from os.path import exists
from collections import defaultdict


import imp





class PersistentLocation(object):
    def __init__(self, mapname):
        self.mapname = mapname
        print ('loading map...')
        self.map, self.size, self.background = load_map(mapname)
        self.position_size = self.size*TILESIZE

        init = imp.load_source('init', LOCATION_PATH %mapname + 'init.py')
        self.generate_func = init.generate

        



    def create_object(self, n, object_type):
        n = int(n/LOCATION_MUL)
        print 'creating %s of %s' % (n, object_type.__name__)
        for i in xrange(n):
            monster = object_type()
            self.new_object(monster)
            
    
        
        



    def load_objects(self):
        if self.location_exists():
            filename = LOCATION_PATH % self.mapname + LOCATION_FILE
            locations_objects = load(filename)


            for object_type, data, (x,y) in locations_objects:
                position = Position(x,y)
                object_type = self.get_class(object_type)

                player = object_type.__load__(proxy(self), *data)

                # if isinstance(player, SavableRandom):
                #     chunk, position = self.choice_position(player)
                #     self.new_object(player, chunk = chunk, position = position)
                # else:
                self.new_object(player, position = position)
            return True
        else:
            return False




    def get_class(self, object_type):
        return getattr(game_objects, object_type)

    def location_exists(self):
        return exists(LOCATION_PATH % self.mapname + LOCATION_FILE)
            
    
    def save(self, force = False):
        if SAVE_LOCATION or force:
            locations_objects = self.save_objects()
            filename = LOCATION_PATH % self.mapname + LOCATION_FILE
            data = dump(locations_objects, filename)



    def save_objects(self):
        objects = []

        for player in self._players.values():
            if isinstance(player, Savable):
                object_type = player.__class__.__name__
                data = player.__save__()
                position = player.position.get()

                objects.append((object_type, data, position))


        return objects





