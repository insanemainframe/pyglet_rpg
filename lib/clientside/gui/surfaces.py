#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import TILESIZE, ROUND_TIMER, HOSTNAME

from share.mathlib import *
from clientside.gui.window import Surface, LEFT_BUTTON, RIGHT_BUTTON

from pyglet.window.key import *



class GameSurface(Surface):
    "разделяемое состояние элементов gui"
    def __init__(self, window, x,y,width, height):
        Surface.__init__(self, x,y,width, height)
        print width, height
        self.rad_h = self.height/2+1
        self.rad_w = self.width/2+1
        
        self.position = Point(0,0)
        self.prev_position = False
        
        self.window = window
        self.destination = False
        
        self.control_keys = [UP, DOWN, LEFT, RIGHT, RSHIFT, SPACE]
        self.vector = Point(0,0)
        self.striking = False

        
        self.step = TILESIZE/2
        self.vector = Point(0,0)
        self.vectors = {UP:Point(0,self.step), DOWN: Point(0,-self.step),
               LEFT : Point(-self.step,0), RIGHT : Point(self.step,0)}
    
    
    def set_camera_position(self, position):
        self.prev_position = self.position
        self.position = position
    
    
    def on_key_press(self, symbol, modifiers):
        "движение с помощью клавиатуры"
        if symbol in self.control_keys:
            self.pressed[symbol] = True
            if symbol==SPACE:
                self.window.client.send_skill()
        else:
            for element in self.elements:
                if element.on_key_press(symbol, modifiers):
                    return True
            return False
    
            
    def on_key_release(self, symbol, modifiers):
        if symbol in self.control_keys:
            del self.pressed[symbol]
        for element in self.elements:
            if element.on_key_release(symbol, modifiers):
                return True
        return False

    def on_mouse_press(self, x, y, button, modifiers):
        if self.window.objects.focus_object:
            focus = self.window.objects.focus_object
            focus_position = self.window.objects.objects[focus].position
        else:
            focus_position = self.position

        if button==RIGHT_BUTTON:
            vector =  Point(x,y) - (self.center - (self.position - focus_position))
            self.window.client.send_ball(vector)
            self.striking = vector
            return True
        else:
            Surface.on_mouse_press(self, x, y, button, modifiers)
    
    
    
    def on_mouse_release(self, x, y, button, modifiers):
        if button==LEFT_BUTTON:
            self.vector = False
        elif button==RIGHT_BUTTON:
            self.striking = False
    
    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if button==LEFT_BUTTON:
            self.vector = (Point(x,y) - self.center)
        elif button==RIGHT_BUTTON:
            self.striking = (Point(x,y) - self.center)
    
    def handle_input(self):
        self.step = self.window.stats.speed
        if self.pressed:
            #получаем список векторов соответствующим нажатым клавишам
            if RSHIFT in self.pressed:
                speed = 2
            else:
                speed = 1
            vectors = [self.vectors[symbol] for symbol in self.pressed if symbol in self.vectors]
            #получаем их сумму и если она не равна нулю - посылаем
            vector = sum(vectors, Point(0,0))*speed
            if vector:
                self.window.client.send_move(vector, self.destination)
                self.destination = False
        elif self.vector:
            self.window.client.send_move(self.vector, self.destination)
        if self.striking:
            self.window.client.send_ball(self.striking)


class StatsSurface(Surface):
    control_keys = []
    def __init__(self, window, x,y,width, height):
        Surface.__init__(self, x,y,width, height)
        self.window = window


    
            



