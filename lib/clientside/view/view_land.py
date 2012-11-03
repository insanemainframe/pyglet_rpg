#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from clientside.gui.gui_lib import Drawable
from clientside.gui.window import create_tile

from share.map import MapTools
from share.point import *

from collections import defaultdict


class LandView(Drawable, MapTools):
    "клиентская карта"
    def __init__(self, window, surface):
        MapTools.__init__(self, 0, 0)
        Drawable.__init__(self)
        self.window = window
        self.surface = surface
        self.accepted = False

        self.observed = set()
        self.tiles = []
        self.map = defaultdict(lambda: defaultdict(lambda: 'fog'))
        self.location_size = 0
        self.background = 'fog'
        self.main_tile = 'fog'
        
        
    def set_location(self, location_size, position, background):
        MapTools.__init__(self, location_size, location_size)
        self.observed = set()
        self.background = background+'_full'
        
        self.location_size = location_size
        self.map = defaultdict(lambda: defaultdict(lambda: 'fog'))
        self.tiles = []
        
        self.surface.set_camera_position(position)
        self.main_tile = background
        self.accepted = True
        print 'New location with background', self.main_tile, background
        
    def move_position(self, vector):
        "перемещаем камеру"
        self.surface.set_camera_position(self.surface.position + vector)
        
    def insert(self, tiles, observed):
        "обновляет карту, добавляя новые тайлы, и видимые на этом ходе тайлы"
        self.observed = observed
        for point, tile_type in tiles:
            self.map[point.x][point.y] = tile_type
            
    def look_around(self):
        "список тайлов в поле зрения"
        rad_h = int(self.surface.rad_h/TILESIZE)+1
        rad_w = int(self.surface.rad_w/TILESIZE)+1
        
        I,J = (self.surface.position/TILESIZE).get()

        range_i = xrange(I-rad_w - 3, I+rad_w+3)
        range_j = xrange(J-rad_h -3, J+rad_h+3)
        
        looked = set()
        for i in range_i:
            for j in range_j:
                position = (Point(i,j)*TILESIZE)-self.surface.position
                if not ((i,j) in self.observed or self.map[i][j]=='fog'):
                    tile = self.map[i][j]+'_fog'
                else:
                    tile = self.map[i][j]
                if tile!=self.main_tile:
                    looked.add((position, tile))
                    
        return looked
    
    def get_shift(self):
        return self.surface.position/TILESIZE*TILESIZE - self.surface.position
        
    def update(self, force=False):
        "обноление на каждом фрейме"
        #если положение не изменилось то ничего не делаем
        if not self.surface.prev_position==self.surface.position or force:
            looked = self.look_around()
            
            self.tiles = [create_tile(point+self.surface.center, tile) for point, tile in looked]
    
    def draw(self):
        x,y = self.get_shift().get()
        self.surface.draw_background(x,y, self.background)
        Drawable.draw(self)

