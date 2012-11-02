#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from zlib import compress, decompress

import os, imp


from marshal import loads, dumps

from collections import Counter

from engine.mathlib import chance
from share.point import Point

from random import randrange, choice



def load_map(mapname): 
    map_file = WORLD_PATH % mapname + MAP_FILE
    map_image = WORLD_PATH % mapname + MAP_IMAGE
    dict_file = WORLD_PATH % mapname + MAP_DICT

    
    if os.path.exists(map_file):
        with open(map_file,'rb') as mapfile:
            tmap = loads(decompress(mapfile.read()))
        
        print('\tmap loaded from pickle')
        tilemap, size, background =  tmap
        return tilemap, size, background

    else:
        print('/data/map.data doesnt exist')
        #gen = Generator()
        gen = FromImage(map_image, dict_file)
        tilemap, size, background = gen.generate()

        
        

        
        
        s = compress(dumps((tilemap, size, background)))

        with  open(map_file,'wb') as mapfile:
            mapfile.write(s)
        
        return tilemap, size, background




tiles = {'water':5, 'stone':5, 'ocean':2}
main_tile = 'grass'

near_cords = [cord.get() for cord in (Point(-1,1),Point(0,1),Point(1,1),
                                    Point(-1,0),             Point(1,0),
                                    Point(-1,-1),Point(0,-1),Point(1,-1))]

class Generator:
    def __init__(self, size=300):
        self.size = size
        self.tiles = {k:int((v/100.0)*(self.size**2)) for k,v in tiles.items()}
        self.tile_map = [[main_tile for j in range(self.size)] for i in range(self.size)]
        self.free = [(i,j) for j in range(self.size) for i in range(self.size)]

    def generate(self):
        for tile, number in self.tiles.items():
            self.apply_tile(tile, number)

        for i, row in enumerate(self.tile_map):
            for j, tile in enumerate(row):
                if not tile:
                    self.tile_map[i][j] = main_tile

        return self.tile_map, self.size, main_tile
        


    def apply_tile(self, tile, number):
        print 'apply_tile', tile, number
        limit = number*(self.size**2)/5
        c = 0
        while number>0 :
            c+=1
            i,j = choice(self.free)
            if c<limit:
                near_counter = 0
                nears = self.get_near(i, j)
                for ni,nj in nears:
                    if self.tile_map[ni][nj]==tile:
                        near_counter +=1
                if near_counter>len(nears)/2:
                    self.tile_map[i][j] = tile
                    number-=1
                    self.free.remove((i,j))
                        
            else:
                self.tile_map[i][j] = tile
                number-=1
                self.free.remove((i,j))



    def get_near(self, I,J):
        cords = [(i+I,j+J) for i,j in near_cords if (0<=i+I<self.size and  0<=j+J<self.size)]
        return cords


class FromImage:
    def __init__(self, map_image, dict_file):
        self.map_image = map_image
        self.dict_file = dict_file

    def generate(self):
        from PIL import Image
        

        tiledict = imp.load_source('tiledict',self.dict_file).tiledict

        counter = Counter()
        image = Image.open(self.map_image)
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
            
        print('\tmap loaded:',size)
        
        background = counter.most_common()[0][0]
        
        return tilemap, size[0], background