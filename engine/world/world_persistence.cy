#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from os.path import exists
from cPickle import load, dump
from copy import copy

from engine.world.map_source import load_map
from engine.enginelib import meta 


class PersistentWorld(object):
    loaded = False
    def __new__(cls, *args, **kwargs):
        inst = object.__new__(cls)
        if cls.world_exists():
            try:
                loaded = cls.load_world()
            except BaseException as error:
                print 'MetaWorld.__new__ error %s' %str(error)
            else:
                inst.loaded = loaded
        return inst

    def __init__(self, mapname):
        self.map, self.size, self.background = load_map(mapname)


    def loading(self):
        data = (self.mapname, self.size, self.size, self.background, len(self.locations), len(self.locations[0]))
        if not self.loaded:
            print('\t creating world "%s": %sx%s background %s locations %sx%s' % data)
        else:
            for player in self.loaded.objects:
                self.new_object(player)
            for player in self.loaded.static_objects:
                self.new_object(player)
           
            print('\t  world "%s" loaded from pickle: %sx%s background %s locations %sx%s' % data)

    @classmethod
    def world_exists(cls):
        return exists(WORLD_PICKLE_PATH % cls.mapname)
    
    @classmethod
    def load_world(cls):
        with open(WORLD_PICKLE_PATH % cls.mapname, 'rb') as w_file:
            world = load(w_file)
            return world
    
    def save(self):
        world = WorldSave(self.players, self.static_objects)
        with open(WORLD_PICKLE_PATH % self.mapname, 'wb') as w_file:
            dump(world, w_file)
            print 'world %s saved' % self.name


class WorldSave:
    def __init__(self, objects, static_objects, ready = False):
        if not ready:
            self.objects = []
            self.static_objects = []
            for player in objects.values():
                if not isinstance(player, meta.Guided):
                    player = copy(player)
                    del player.world
                    del player.location
                    self.objects.append(player)
            for player in static_objects.values():
                player = copy(player)
                del player.world
                del player.location 
                self.static_objects.append(player)
        else:
            self.objects = objects
            self.static_objects = static_objects