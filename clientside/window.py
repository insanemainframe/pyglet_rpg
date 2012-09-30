#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyglet.image.codecs.png import PNGImageDecoder


import pyglet
from pyglet.gl import *
from pyglet.window import Window as GUIWindow


from time import time
from os import walk
from os.path import join
from collections import defaultdict

from share.mathlib import Point,NullPoint

from config import TILESIZE, TILESDIR, ROUND_TIMER, HOSTNAME



def create_label(text, point):
    layer = 1
    return (layer, text, point, 'label')

def create_tile(point, tilename, layer=1):
    "создае тайл"
    return (layer, tilename, point, 'tile')

########################################################################
class GameWindow():
    "разделяемое состояние элементов gui"
    def __init__(self, width, height):
        cls = GameWindow
        
        cls.width = width
        cls.height = height
        cls.center = Point(cls.width/2,cls.height/2)
        cls.rad_h = cls.height/2
        cls.rad_w = cls.width/2
        cls.clock_setted = False
        cls.complete = 0
        cls.position = Point(0,0)
        cls.prev_position = False
        cls.gentiles()
        
    @staticmethod
    def gentiles():
        cls = GameWindow
        cls.unknown = pyglet.image.load(join(TILESDIR, 'unknown.png'), decoder=PNGImageDecoder()).get_texture()
        
        cls.tiledict = defaultdict(lambda: cls.unknown)
        for root, subfolders, files in walk(TILESDIR):
            for image_file in files:
                image = pyglet.image.load(join(root,image_file), decoder=PNGImageDecoder()).get_texture()
                tilename = image_file[:-4]
                cls.tiledict[tilename] = image
    
    @staticmethod
    def set_camera_position(position):
        GameWindow.prev_position = GameWindow.position
        GameWindow.position = position
    
    
    def enable_alpha(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    @staticmethod
    def set_round_update(func, timer_value):
        pyglet.clock.schedule_interval(func, timer_value)
    
    @staticmethod
    def set_update(func):
            pyglet.clock.schedule(func)
    
    @staticmethod
    def run_app():
        pyglet.app.run()
        
    @staticmethod
    def draw_tile(tilename, x,y, width, height):
        GameWindow.tiledict[tilename].blit(x,y, width=width, height=height)
    
    @staticmethod
    def draw_label(text, font_name, font_size, x,y, anchor_x='center', anchor_y='center'):
        pyglet.text.Label(text,
                          font_name=font_name,
                          font_size=font_size,
                          x=x, y=y,
                          anchor_x=anchor_x, anchor_y=anchor_y).draw()
