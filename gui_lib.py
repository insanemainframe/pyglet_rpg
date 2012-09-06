#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import TILESIZE
from mathlib import Point
from pyglet.window.key import UP, DOWN, LEFT, RIGHT

from time import time

class TimerObject:
    "объект с таймером и deltatime"
    def __init__(self, timer_value):
        self.timer_value = timer_value
    
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
    def on_key_press(self, symbol, modifiers):
        "движение с помощью клавиатуры"
        if symbol==UP: self.vector = Point(0,41)
        elif symbol==DOWN: self.vector = Point(0,-40)
        elif symbol==LEFT: self.vector = Point(-40,0)
        elif symbol==RIGHT: self.vector = Point(40,0)
    
    def on_mouse_press(self, x, y, button, modifiers):
        "перехватывавем нажатие мышки"
        #левая кнопка - движение
        if button==1:
            vector = (Point(x,y) - self.center)
            self.vector = vector
            
class Drawable:
    "рисуемые объекты"
    def draw(self):
        [self.tiledict[tilename].blit(x,y, width=TILESIZE, height=TILESIZE) for tilename, (x,y) in self.tiles]
