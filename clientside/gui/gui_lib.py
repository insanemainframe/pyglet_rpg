#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import time

from share.mathlib import Point


from config import TILESIZE, ROUND_TIMER
from client_config import *


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

########################################################################

            

class Drawable:
    "рисуемые объекты"
    def __init__(self):
        self.shift = Point()
        self.tiles = []
    
    def draw(self):
        self.tiles.sort(lambda x,y: -1 if x[0]>y[0] else 1)
        
        try:
            for layer,tilename, position, sprite_type, hover in self.tiles:
                if sprite_type=='tile':
                    x,y = (position-self.shift).get()
                    if -TILESIZE<x<self.surface.width+TILESIZE and -TILESIZE<y<self.surface.height+TILESIZE:
                        self.surface.draw_tile(tilename, x,y, hover)
                        
                elif sprite_type=='label':
                    
                    x,y = (position-self.shift).get()
                    self.surface.draw_label(tilename,10, x,y)
        except ValueError as error:
            print self.tiles
            raise error
                


