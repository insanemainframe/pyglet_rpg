#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import time

from share.mathlib import Point,NullPoint
from clientside.window import GameWindow, create_tile


from config import TILESIZE, ROUND_TIMER





        

########################################################################            
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

            

class Drawable(GameWindow):
    "рисуемые объекты"
    def __init__(self):
        self.animation = 1
        self.animation_counter = 0
        self.aps = 15
        self.shift = NullPoint
    
    def draw(self):
        self.tiles.sort(lambda x,y: -1 if x[0]>y[0] else 1)
        
        for layer,tilename, position, sprite_type in self.tiles:
            if sprite_type=='tile':
                width = self.tiledict[tilename].width
                height = self.tiledict[tilename].height
                shift =  Point(width/2, height/2)
                x,y = (position-shift-self.shift).get()
                if -TILESIZE<x<self.width and -TILESIZE<x<self.height:
                    self.draw_tile(tilename, x,y, width, height)
                    
            elif sprite_type=='label':
                height = self.tiledict['player'].height
                shift =  Point(0, height/2)
                x,y = (position-shift-self.shift).get()
                self.draw_label(tilename,'Times New Roman', 10, x,y,)
                


