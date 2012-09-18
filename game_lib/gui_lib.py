#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyglet.window.key import UP, DOWN, LEFT, RIGHT
from pyglet.image.codecs.png import PNGImageDecoder
import pyglet

from abc import ABCMeta, abstractmethod, abstractproperty
from time import time
from os import listdir

from math_lib import Point

from config import TILESIZE, TILESDIR, ANIMATED_TILES, ROUND_TIMER, HOSTNAME


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
        names = listdir(TILESDIR)
        cls.tiledict = {}
        for name in names:
            image = pyglet.image.load(TILESDIR+name, decoder=PNGImageDecoder()).get_texture()
            cls.tiledict[name[:-4]] = image
    
    @staticmethod
    def set_camera_position(position):
        GameWindow.prev_position = GameWindow.position
        GameWindow.position = position
        
            
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
    pressed = {}
    def send_vector():
        ""
    def __init__(self):
        step = TILESIZE/2
        self.vectors = {UP:Point(0,step), DOWN: Point(0,-step),
                        LEFT : Point(-step,0), RIGHT : Point(step,0)}
        self.control_keys = [UP, DOWN, LEFT, RIGHT]
            
    def on_key_press(self, symbol, modifiers):
        "движение с помощью клавиатуры"
        if symbol in self.control_keys:
            self.pressed[symbol] = True
            
    
    def on_key_release(self, symbol, modifiers):
        if symbol in self.control_keys:
            del self.pressed[symbol]
        
    def on_mouse_press(self, x, y, button, modifiers):
        "перехватывавем нажатие левой кнопки мышки"
        #левая кнопка - движение
        print 'mouse press'
        if button==1:
            self.vector = (Point(x,y) - self.center)
            
        elif button==4:
            vector = (Point(x,y) - self.center)
            self.send_ball(vector)
    
    def on_mouse_release(self, x, y, button, modifiers):
        if button==1:
            self.vector = False
    
    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if button==1:
            self.vector = (Point(x,y) - self.center)
            
        
    
    def handle_input(self):
        if self.pressed:
            #получаемсписок векторов соответствующим нажатым клавишам
            vectors = [self.vectors[symbol] for symbol in self.pressed if symbol in self.vectors]
            #получаем их сумму и если она не равна нулю - посылаем
            vector = sum(vectors, Point(0,0))
            if vector:
                self.send_move(vector)
        elif self.vector:
            self.send_move(self.vector)
            

class Drawable:
    "рисуемые объекты"
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
    

    
