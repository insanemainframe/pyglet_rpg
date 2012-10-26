#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from zlib import compress, decompress

import os, imp

try:
    from cPickle import loads, dumps
except ImportError:
    from pickle import loads, dumps

from collections import Counter




def load_map(mapname): 
    map_file = WORLD_PATH % mapname + 'map.data'
    map_image = WORLD_PATH % mapname + 'map.png'
    dict_file = WORLD_PATH % mapname + 'tiledict.py'

    
    if os.path.exists(map_file):
        mapfile = open(map_file,'r')
        tmap = loads(decompress(mapfile.read()))
        mapfile.close()
        print('\tmap loaded from pickle')
        tilemap, size, background =  tmap
        return tilemap, size, background

    else:
        print('/data/map.data doesnt exist')
        from PIL import Image
        

        tiledict = imp.load_source('tiledict',dict_file).tiledict

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
            
        print('\tmap loaded:',size)
        
        mapfile = open(map_file,'w')
        background = counter.most_common()[0][0]
        
        s = compress(dumps((tilemap, size[0], background)))
        mapfile.write(s)
        mapfile.close()
        
        return tilemap, size[0], background
