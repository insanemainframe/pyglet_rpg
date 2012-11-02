#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from os.path import exists
from zlib import compress, decompress
from marshal import loads, dumps

from engine.world.map_source import load_map
from engine.enginelib import meta 
from engine import game_objects

class PersistentWorld(object):
    def __init__(self, mapname):
        self.mapname = mapname
        print 'loading map...'
        self.map, self.size, self.background = load_map(mapname)
        



    def load_objects(self):
        if self.world_exists():
            with open(WORLD_PATH % self.mapname + WORLD_FILE, 'rb') as w_file:
                data = w_file.read()
            worlds_objects = loads(decompress(data))

            for object_type, data in worlds_objects:
                object_type = self.get_class(object_type)
                data = object_type.__load__(*data)
                player = object_type(*data)
                self.new_object(player)
            return True
        else:
            return False




    def get_class(self, object_type):
        return getattr(game_objects, object_type)

    def world_exists(self):
        return exists(WORLD_PATH % self.mapname + WORLD_FILE)
            
    
    def save(self, force = False):
        if SAVE_WORLD or force:
            worlds_objects = self.save_objects()
            data = compress(dumps(worlds_objects))
            with open(WORLD_PATH % self.mapname + WORLD_FILE, 'wb') as w_file:
                w_file.write(data)
                print 'world %s saved' % self.name


    def save_objects(self):
        objects = []

        for player in self.players.values():
            if isinstance(player, meta.Savable):
                object_type = player.__class__.__name__
                data = player.__save__()

                objects.append((object_type, data))


        return objects


