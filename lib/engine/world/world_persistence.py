#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from os.path import exists
from zlib import compress, decompress
from marshal import loads, dumps

from engine.world.map_source import load_map
from engine.enginelib import meta 
from engine import game_objects
from share.logger import print_log


PICKLE_PATH = '%sworld.marshal.zlib' % WORLD_PATH

class PersistentWorld(object):
    def __init__(self, mapname):
        self.mapname = mapname
        print_log('loading map %s ...' % self.mapname)
        self.map, self.size, self.background = load_map(mapname)
        



    def load_objects(self):
        if self.world_exists():
            print_log('Loading world %s from pickle' % self.name)
            with open(PICKLE_PATH % self.mapname, 'rb') as w_file:
                data = w_file.read()
            worlds_objects = loads(decompress(data))

            for object_type, data in worlds_objects:
                #print_log 'loading', object_type, data
                object_type = self.get_class(object_type)
                data = object_type.__load__(*data)
                player = object_type(*data)
                self.new_object(player)
            return True
        else:
            print_log("world pickle doesn't exist")
            return False




    def get_class(self, object_type):
        return getattr(game_objects, object_type)

    def world_exists(self):
        return exists(PICKLE_PATH % self.mapname)
            
    
    def save(self, force = False):
        if force:
            worlds_objects = self.save_objects()
            data = compress(dumps(worlds_objects))
            with open(PICKLE_PATH % self.mapname, 'wb') as w_file:
                w_file.write(data)
                print_log('world %s saved' % self.name)


    def save_objects(self):
        objects = []

        for player in self.static_objects.values():
            if isinstance(player, meta.Savable):
                object_type = player.__class__.__name__
                data = player.__save__()

                objects.append((object_type, data))

        for player in self.players.values():
            if isinstance(player, meta.Savable):
                object_type = player.__class__.__name__
                data = player.__save__()

                objects.append((object_type, data))


        return objects


