#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.serialization import loads, dumps, load, dump

import os, imp


from collections import Counter

from engine.mathlib import Cord, Position, ChunkCord, chance
from engine.world.objects_containers import near_cords
from engine.world.surfaces import tiledict

from random import randrange, choice



def load_map(mapname): 
    map_file = LOCATION_PATH % mapname + MAP_FILE
    map_image = LOCATION_PATH % mapname + MAP_IMAGE

    
    if os.path.exists(map_file):
        map_data = load(map_file)
        
        tilemap, size, background =  map_data

        print('\tmap loaded from pickle')
        return tilemap, size, background

    else:
        print('/data/map.data doesnt exist')
        #gen = Generator()
        gen = FromImage(map_image)

        tilemap, size, background = gen.generate()
        map_data = tilemap, size, background

        source = dump(map_data, map_file)

        
        return tilemap, size, background




tiles = {'water':5, 'stone':5, 'ocean':2}
main_tile = 'grass'



class Generator:
    def __init__(self, size=300):
        self.size = size
        self.voxels = {k:int((v/100.0)*(self.size**2)) for k,v in tiles.items()}
        self.tile_map = [[main_tile for j in range(self.size)] for i in range(self.size)]
        self.free = [(i,j) for j in range(self.size) for i in range(self.size)]

    def generate(self):
        for tile, number in self.voxels.items():
            self.apply_tile(tile, number)

        for i, row in enumerate(self.tile_map):
            for j, tile in enumerate(row):
                if not tile:
                    self.tile_map[i][j] = main_tile

        return self.tile_map, self.size, main_tile
        


    def apply_tile(self, tile, number):
        print( 'apply_tile', tile, number)
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
    def __init__(self, map_image,):
        self.map_image = map_image

    def generate(self):
        from PIL import Image
        


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
                row.append(unicode(tile))
            tilemap.append(row)
            
       
        
        background = counter.most_common()[0][0]
        print('\tmap loaded:',size, background)
        
        return tilemap, size[0], background