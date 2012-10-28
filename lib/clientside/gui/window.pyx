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

from share.point import Point

from config import TILESIZE, ROUND_TIMER, HOSTNAME
from client_config import TILESDIR


LEFT_BUTTON = 1
RIGHT_BUTTON = 4

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
        return (layer, text, point, 'label', False)

def create_tile(point, tilename, layer=1, hover = False):
        "создае тайл"
        return (layer, tilename, point, 'tile', hover)

class Surface:
    inited = False
    @classmethod
    def init_cls(self):
        if not Surface.inited:
            self.gentiles()
            Surface.inited = True
            self.pressed = {}
    
    def __init__(self, x,y,width, height):
        self.x, self.y = x,y
        self.width = width
        self.height = height
        self.center = Point(width/2, height/2)
        self.elements = []
    
    def __contains__(self, point):
        x,y = point.get()
        if self.x<x<self.x+self.width and self.y < y < self.y +self.height:
            return True
        else:
            return False
    
    def bind(self, element):
        self.elements.append(element)
    
    @classmethod
    def gentiles(self):
        
        self.unknown = pyglet.image.load(join(TILESDIR, 'unknown.png'), decoder=PNGImageDecoder()).get_texture()
        
        self.tiledict = defaultdict(lambda: self.unknown)
        for root, subfolders, files in walk(TILESDIR):
            for image_file in files:
                image = pyglet.image.load(join(root,image_file), decoder=PNGImageDecoder()).get_texture()
                tilename = image_file[:-4]
                self.tiledict[tilename] = image.get_texture()
    
    def draw_tile(self, tilename, x,y, hover = False):
        x,y = self.x+x, self.y+y
        if hover:
            mul = 1.2
        else:
            mul = 1
        twidth = self.tiledict[tilename].width
        theight = self.tiledict[tilename].height
        
        width = twidth * mul
        height = theight * mul
        
        tile = self.tiledict[tilename]
        x,y = x-twidth/2, y - theight/2
        #glBindTexture(texture.target, texture.id)
        
        self.tiledict[tilename].blit(x,y, width=width, height=height)
    
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
    
    def on_key_press(self, symbol, modifiers):
        for element in self.elements:
            if element.on_key_press(symbol, modifiers):
                return True
        return False
    
    def on_key_release(self, symbol, modifiers):
        for element in self.elements:
            if element.on_key_release(symbol, modifiers):
                return True
        return False
    
    def handle_input(self):
        return False
    
    def on_mouse_motion(self, x, y, dx, dy):
        for element in self.elements:
            if element.on_mouse_motion(x, y, dx, dy):
                return True
        return False
    def on_mouse_press(self, x, y, button, modifiers):
        for element in self.elements:
            if element.on_mouse_press(x, y, button, modifiers):
                return True
        return False
    
    def on_mouse_release(self, x, y, button, modifiers):
        for element in self.elements:
            if element.on_mouse_release(x, y, button, modifiers):
                return True
        return False
        
    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        for element in self.elements:
            if element.on_mouse_drag(x, y, dx, dy, button, modifiers):
                return True
        return False
    
    

Surface.init_cls()


class GuiElement:
    control_key = ()
    def __init__(self, surface):
        self.surface = surface
        self.pressed = {}
        surface.bind(self)
        
    def on_key_press(self, symbol, modifiers):
        return False
        
    def on_key_release(self, symbol, modifiers):
        return False
    
    def on_mouse_motion(self, x, y, dx, dy):
        return False
    
    def on_mouse_press(self, x, y, button, modifiers):
        return False
    
    def on_mouse_release(self, x, y, button, modifiers):
        return False
        
    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        return False

    
   

   
    
class Label(pyglet.text.Label):
    def __init__(self, surface, text, x, y, archor = True):
        x,y = surface.x+x, surface.y+y
        if archor:
            kwargs = dict(anchor_x='center', anchor_y='center')
        else:
            kwargs = {}
        pyglet.text.Label.__init__(self, text,
                              font_name='Times New Roman',
                              font_size=13,
                              x=x, y=y,
                              **kwargs)

class TextLabel(pyglet.text.HTMLLabel):
    def __init__(self, surface, text, x,y, width = False):
        x,y = surface.x+x, surface.y+y
        text = text
        if width:
            kwargs = {'multiline':True, 'width' : width}
        else:
            kwargs = {}

        pyglet.text.HTMLLabel.__init__(self, text, x=x, y=y, **kwargs)


ClockDisplay = pyglet.clock.ClockDisplay
