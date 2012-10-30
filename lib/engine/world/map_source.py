#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from zlib import compress, decompress

import os, imp

from marshal import loads, dumps

from collections import Counter




def load_map(mapname): 
    map_file = WORLD_PATH % mapname + 'map.marshal.zlib'
    map_image = WORLD_PATH % mapname + 'map.png'
    dict_file = WORLD_PATH % mapname + 'tiledict.py'

    
    if os.path.exists(map_file):
        with  open(map_file,'rb') as mapfile:
            readed = mapfile.read()
        try:
            decompressed = decompress(readed)
            tmap = loads(decompressed)
        except Exception as error:
            print('Error: "%s" while loading %s' % (error, map_file))
        else:
            print('\t map loaded from data file')
            tilemap, size, background =  tmap
            return tilemap, size, background
    else:
        print("\t map data file doesn't exist")

    print('Generating tilemap "for" %s' % mapname)
    from PIL import Image
    

    tiledict = imp.load_source('tiledict',dict_file).tiledict

    counter = Counter()
    image = Image.open(map_image)
    size = image.size
    m = image.load()
    
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

    saved_map = bytes(compress(dumps((tilemap, size[0], background))))

    with open(map_file,'wb') as mapfile:
        mapfile.write(saved_map)
    
    return tilemap, size[0], background
