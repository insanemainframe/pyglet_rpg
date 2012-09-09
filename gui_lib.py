#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import TILESIZE, ANIMATED_TILES, ROUND_TIMER
from math_lib import Point
from pyglet.window.key import UP, DOWN, LEFT, RIGHT
import pyglet

from time import time

def create_label(text, point):
    x,y = point.get()
    return (text, point.get(), 'label')

def create_tile(point, tilename):
        "создае тайл"
        return (tilename, point.get(), None)

def create_loading(point):
    x,y = point.get()
    return pyglet.text.Label('Waiting for server response',
                          font_name='Times New Roman',
                          font_size=10,
                          x=x, y=y,
                          anchor_x='center', anchor_y='center').draw()
class TimerObject:
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
    def __init__(self):
        self.animation = 1
        self.animation_counter = 0
        self.aps = 15
    
    def animation_tick(self):
        if self.animation_counter==self.aps:
            self.animation*=-1
            self.animation_counter = 0
        self.animation_counter+=1
            
        self.animation*=-1
    def draw(self):
        for tilename, (x,y), tiletype in self.tiles:
            if tilename in ANIMATED_TILES:
                if self.animation==-1:
                    tilename = tilename+'_'
                self.animation_tick()
            if tiletype:
                pyglet.text.Label(tilename,
                          font_name='Times New Roman',
                          font_size=10,
                          x=x, y=y,
                          anchor_x='center', anchor_y='center').draw()
            else:
                self.tiledict[tilename].blit(x,y, width=TILESIZE, height=TILESIZE)
    

    
