#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from clientside.gui.gui_lib import Drawable
from clientside.gui.window import GameWindow, create_tile

from share.map import MapTools
from share.mathlib import *

from collections import defaultdict


class LandView(GameWindow,  Drawable, MapTools):
    "клиентская карта"
    def __init__(self, world_size, position):
        MapTools.__init__(self, world_size, world_size)
        Drawable.__init__(self)
        GameWindow.observed = set()
        
        self.world_size = world_size
        self.map = defaultdict(lambda: defaultdict(lambda: 'fog'))
        self.tiles = []
        
        self.set_camera_position(position)
        self.prev_position = position/2
        self.main_tile = 'grass'
        
        
        
    def move_position(self, vector):
        "перемещаем камеру"
        self.set_camera_position(self.position + vector)
        
    def insert(self, tiles, observed):
        "обновляет карту, добавляя новые тайлы, и видимые на этом ходе тайлы"
        self.observed = observed
        for point, tile_type in tiles:
            self.map[point.x][point.y] = tile_type
            
    def look_around(self):
        "список тайлов в поле зрения"
        rad_h = int(self.rad_h/TILESIZE)
        rad_w = int(self.rad_w/TILESIZE)
        
        I,J = (self.position/TILESIZE).get()

        range_i = xrange(I-rad_w-1, I+rad_w+2)
        range_j = xrange(J-rad_h-1, J+rad_h+2)
        
        looked = set()
        for i in range_i:
            for j in range_j:
                position = (Point(i,j)*TILESIZE)-self.position
                if not ((i,j) in self.observed or self.map[i][j]=='fog'):
                    tile = self.map[i][j]+'_fog'
                else:
                    tile = self.map[i][j]
                if tile!=self.main_tile:
                    looked.add((position, tile))
                    
        return looked
    
    def get_shift(self):
        return self.position/TILESIZE*TILESIZE - self.position
        
    def update(self):
        "обноление на каждом фрейме"
        #если положение не изменилось то ничего не делаем
        if not self.prev_position==self.position:
            looked = self.look_around()
            
            self.tiles = [create_tile(point+self.center, tile) for point, tile in looked]
    
    def draw(self):
        x,y = self.get_shift().get()
        self.draw_background(x,y)
        Drawable.draw(self)

