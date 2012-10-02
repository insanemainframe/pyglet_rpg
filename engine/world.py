#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from mapgen import load_map

class World:
    "класс карты как со стороны ссервера"
    def __init__(self, game):
        World.map, World.size = load_map()
        print 'server world size',World.size
        self.game = game
    
    def loc_cord_valid(self, cord):
        size = self.size * LOCATIONSIZE
        if 0<cord.x<size and 0<cord.y<size:
            return True
        else:
            return False
        
        
    



        

