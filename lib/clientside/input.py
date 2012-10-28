#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.point import Point


class InputHandle:
    "перехват устройств ввода"
    
    striking = False
    
    def __init__(self):
        pass
    
    
    def on_key_press(self, symbol, modifiers):
        for surface in self.surfaces:
            if surface.on_key_press(symbol, modifiers):
                return True
        return False
    
    def on_key_release(self, symbol, modifiers):
        for surface in self.surfaces:
            if surface.on_key_release(symbol, modifiers):
                return True
        return False
    
    
    def on_mouse_motion(self, x, y, dx, dy):
        for surface in self.surfaces:
            if Point(x,y) in surface:
                surface.on_mouse_motion(x, y, dx, dy)
    
    def on_mouse_press(self, x, y, button, modifiers):
        "перехватывавем нажатие левой кнопки мышки"
        for surface in self.surfaces:
            if Point(x,y) in surface:
                surface.on_mouse_press(x, y, button, modifiers)
    
    def on_mouse_release(self, x, y, button, modifiers):
        for surface in self.surfaces:
            if Point(x,y) in surface:
                surface.on_mouse_release(x, y, button, modifiers)
    
    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        for surface in self.surfaces:
            if Point(x,y) in surface:
                surface.on_mouse_drag(x, y, dx, dy, button, modifiers)
    
    def handle_input(self):
        for surface in self.surfaces:
            surface.handle_input()
            
    
