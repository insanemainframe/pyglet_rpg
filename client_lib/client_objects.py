#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from sys import path
path.append('../')

from gui_lib import create_tile, create_label

from game_lib.math_lib import Point, NullPoint

from config import TILESIZE

class Object:
    "класс игрового объекта на карте"
    def __init__(self, name, position, tilename):
        print 'create %s' % name
        self.position = position
        self.name = name
        self._tilename = tilename
        self.tilename = tilename
        self.moving = False
        self.animation = 1
    
    def draw(self, shift):
        position = self.position - shift - Point(TILESIZE/2,TILESIZE/2)
        if self.moving:
            if self.animation>0:
                tilename = self.tilename+'_move'
            else:
                tilename = self.tilename+'_move_'
            self.animation*=-1
        else:
            tilename = self.tilename
        tiles = [create_tile(position, tilename)]
        if self.tilename not in ['ball','ball_move']:
                label = create_label(self.name, position)
                tiles.append(label)
        return tiles
    
    def update(self):
        if self.moving:
            self.moving = False
            
    def move(self, vector):
        if vector:
            self.moving = True
            self.position +=vector

    
    def __del__(self):
        print 'remove %s' % self.name
