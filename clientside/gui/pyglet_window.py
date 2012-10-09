#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyglet.image.codecs.png import PNGImageDecoder


import pyglet
from pyglet.gl import *
from pyglet.window import Window


from time import time
from os import walk
from os.path import join
from collections import defaultdict

from share.mathlib import Point,NullPoint

from config import TILESIZE, TILESDIR, ROUND_TIMER, HOSTNAME


class GUIWindow(Window):
    def __init__(self, height, width):
        Window.__init__(self, height, width)
        self.clock_setted = False
        self.complete = 0
        self.center = Point(height/2, width/2)
    
    def enable_alpha(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    def set_round_update(self, func, timer_value):
        pyglet.clock.schedule_interval(func, timer_value)
    
    def set_update(self, func):
        pyglet.clock.schedule(func)
    
    def run_app(self):
        pyglet.app.run()


########################################################################

def create_label(text, point):
        layer = 1
        return (layer, text, point, 'label')

def create_tile(point, tilename, layer=1):
        "создае тайл"
        return (layer, tilename, point, 'tile')

class Surface:
    inited = False
    @classmethod
    def init_cls(self):
        if not Surface.inited:
            self.gentiles()
            Surface.inited = True
    
    def __init__(self, x,y,width, height):
        self.x, self.y = x,y
        self.width = width
        self.height = height
        self.center = Point(width/2, height/2)
    
    @classmethod
    def gentiles(self):
        self.unknown = pyglet.image.load(join(TILESDIR, 'unknown.png'), decoder=PNGImageDecoder()).get_texture()
        
        self.tiledict = defaultdict(lambda: self.unknown)
        for root, subfolders, files in walk(TILESDIR):
            for image_file in files:
                image = pyglet.image.load(join(root,image_file), decoder=PNGImageDecoder()).get_texture()
                tilename = image_file[:-4]
                self.tiledict[tilename] = image
    
    def draw_tile(self, tilename, x,y):
        x,y = self.x+x, self.y+y
        width = self.tiledict[tilename].width
        height = self.tiledict[tilename].height
        self.tiledict[tilename].blit(x-width/2,y-height/2, width=width, height=height)
    
    def draw_label(self, text,font_size, x,y):
        x,y = self.x+x, self.y+y
        font_name = 'Times New Roman'
        height = self.tiledict['player'].height
        pyglet.text.Label(text,
                          font_name=font_name,
                          font_size=font_size,
                          x=x, y=y-height/2,
                          anchor_x='center', anchor_y='center').draw()
    
    def draw_background(self, x,y, tilename):
        x,y = self.x+x, self.y+y
        self.tiledict[tilename].blit(x,y)
    
    

Surface.init_cls()

class GameSurface(Surface):
    "разделяемое состояние элементов gui"
    def __init__(self, x,y,width, height):
        Surface.__init__(self, x,y,width, height)
        self.rad_h = self.height/2
        self.rad_w = self.width/2
        
        self.position = Point(0,0)
        self.prev_position = False
        
    
    def set_camera_position(self, position):
        self.prev_position = self.position
        self.position = position
    


class StatsSurface(Surface):
    def __init__(self, x,y,width, height):
        Surface.__init__(self, x,y,width, height)
    
   
   
    
class Label(pyglet.text.Label):
    def __init__(self, surface, text, x,y):
        x,y = surface.x+x, surface.y+y
        print x,y
        pyglet.text.Label.__init__(self, text,
                              font_name='Times New Roman',
                              font_size=13,
                              x=x, y=y,
                              anchor_x='center', anchor_y='center')




ClockDisplay = pyglet.clock.ClockDisplay
