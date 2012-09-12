#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyglet.window.key import UP, DOWN, LEFT, RIGHT
from pyglet.image.codecs.png import PNGImageDecoder
import pyglet

from abc import ABCMeta, abstractmethod, abstractproperty
from time import time
from os import listdir
import re

from math_lib import Point

from config import TILESIZE, ANIMATED_TILES, ROUND_TIMER, HOSTNAME


def create_label(text, point):
    x,y = point.get()
    return (text, point.get(), 'label')

def create_tile(point, tilename):
        "создае тайл"
        return (tilename, point.get(), None)

class LoadingScreen:
    def __init__(self, point):
        x,y = point.get()
        self.label = pyglet.text.Label('Waiting for server response',
                          font_name='Times New Roman',
                          font_size=10,
                          x=x, y=y,
                          anchor_x='center', anchor_y='center')
    def draw(self):
        self.label.draw()

class GameWindow():
    "разделяемое состояние элементов gui"
    @staticmethod
    def configure(width, height):
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
        
    @staticmethod
    def gentiles():
        cls = GameWindow
        names = listdir('images')
        cls.tiledict = {}
        for name in names:
            image = pyglet.image.load('images/%s' % name, decoder=PNGImageDecoder()).get_texture()
            cls.tiledict[name[:-4]] = image
    
    @staticmethod
    def set_camera_position(position):
        GameWindow.prev_position = GameWindow.position
        GameWindow.position = position

class AskHostname:
    def __init__(self):
        self.default = HOSTNAME
        self.pattern = '^\d+\.\d+\.\d+\.\d+$'
        message = 'Enter hostname or press Enter for default %s: ' % HOSTNAME
        while 1:
            result = raw_input(message)
            if not result:
                self.hostname = self.default
                break
            elif self.check(result):
                self.hostname = result
                break
            else:
                print 'invalid value: %s' % self.error
    
    def check(self, message):
        if re.match(self.pattern, message):
            return True
        else:
            self.error = 'wrong format'        
            return False
        
            
class DeltaTimerObject:
    "объект с таймером и deltatime"
    def __init__(self):
        self.timer_value = ROUND_TIMER
    
    def set_timer(self):
        self.clock = time()
        self.complete = 0
        self.clock_setted = True
    
    def complete_delta(self):
        if self.complete<1:
            delta = 1-self.complete
            self.complete = 1
            return delta
        else:
            return 0
    
    def get_delta(self):
        "возвращзает отношение времени предыдщего вызова get_delta или set_timer к timer_value"
        if self.clock_setted:
            cur_time = time()
            delta_time = cur_time-self.clock
            part = delta_time/self.timer_value
            self.clock = cur_time
            if part+self.complete<=1:
                self.complete+=part
                return part
            else:
                part = 1-self.complete
                self.complete = 1
                return part
        else:
            return 0

class InputHandle:
    "перехват устройств ввода"
    #__metaclass__=ABCMeta
    @abstractmethod
    def send_vector():
        ""
    def __init__(self):
        self.vectors = {UP:Point(0,40), DOWN: Point(0,-40), LEFT : Point(-40,0), RIGHT : Point(40,0)}
            
    def on_key_press(self, symbol, modifiers):
        "движение с помощью клавиатуры"
        if symbol in (UP,DOWN, LEFT,RIGHT):
            self.send_vector(self.vectors[symbol])
    
    def on_mouse_press(self, x, y, button, modifiers):
        "перехватывавем нажатие мышки"
        #левая кнопка - движение
        if button==1:
            vector = (Point(x,y) - self.center)
            self.send_vector(vector)
        
            
class Drawable:
    "рисуемые объекты"
    #__metaclass__ = ABCMeta
    @abstractproperty
    def tiles():
        ""
    def __init__(self):
        self.animation = 1
        self.animation_counter = 0
        self.aps = 15
    
    def draw(self):
        for tilename, (x,y), tiletype in self.tiles:

            if tiletype:
                pyglet.text.Label(tilename,
                          font_name='Times New Roman',
                          font_size=10,
                          x=x, y=y,
                          anchor_x='center', anchor_y='center').draw()
            else:
                self.tiledict[tilename].blit(x,y, width=TILESIZE, height=TILESIZE)
    

    
