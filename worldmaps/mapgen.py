#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import choice, randrange
from zlib import compress, decompress

def generate(size):
    tileset =  [tile[:-4] for tile in listdir('data')]
    tileset.remove('player')
    tileset.remove('fog')
    tmap = Generator(size, 'water', 'grass').tmap
    tmap = Generator(size, 'water', 'forest', tmap, ['water']).tmap
    
    return tmap

class Generator:
    def __init__(self,size, default, tile, tmap =None, ignore =[]):
        self.size= size
        self.ignore = ignore
        if not tmap:
            tmap = [[default for j in range(size)] for i in range(size)]
        self.tmap = tmap
        self.setseeds(size)
        for seed in self.seeds:
            self.drawseed(seed, randrange(int(self.size/30)), tile)
        
    def setseeds(self, number):
        self.seeds = []
        for i in range(number):
            point = (randrange(self.size), randrange(self.size))
            self.seeds.append(point)
    
    def drawseed(self, seed, rad, tile):
        x,y = seed
        for i in range(x-rad,x+rad):
            for j in range(y-rad, x+rad):
                try:
                    if self.tmap[i][j] not in self.ignore:
                        self.tmap[i][j] = tile
                except IndexError:
                    pass
    
import os, imp
from cPickle import loads, dumps
from collections import Counter




def load_map(mapname): 
    map_file = 'worldmaps/%s/map.data' % mapname
    map_image = 'worldmaps/%s/map.png' % mapname
    dict_file = 'worldmaps/%s/tiledict.py' % mapname
    tiledict = imp.load_source('tiledict',dict_file).tiledict
    if os.path.exists(map_file):
        mapfile = open(map_file,'r')
        tmap = loads(decompress(mapfile.read()))
        mapfile.close()
        print 'map loaded from pickle'
        return tmap
    
    print '/data/map.data doesnt exist'
    from PIL import Image
    
    counter = Counter()
    image = Image.open(map_image)
    size = image.size
    m =image.load()
    tilemap =[]
    for i in range(size[0]):
        row=[]
        for j in range(size[1]):
            color = m[i,j][:3]
            tile = tiledict[color]
            counter[tile]+=1
            row.append(tile)
        tilemap.append(row)
    print 'map loaded',size
    mapfile = open(map_file,'w')
    background = counter.most_common()[0][0]
    s = compress(dumps((tilemap, size[0], background)))
    mapfile.write(s)
    mapfile.close()
    return tilemap, size[0], background
