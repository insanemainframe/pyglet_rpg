#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *

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

class GameWindow():
    "разделяемое состояние элементов gui"
    def __init__(self, width, height):
        cls = GameWindow
        
        pygame.init()
        window = pygame.display.set_mode((height, width))
        pygame.display.set_caption('mygame')
        
        cls.screen = window
        
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

        cls.unknown = pygame.image.load(join(TILESDIR, 'unknown.png')).convert_alpha()
        
        cls.tiledict = defaultdict(lambda: cls.unknown)
        for root, subfolders, files in walk(TILESDIR):
            for image_file in files:
                image = pygame.image.load(join(root, image_file)).convert_alpha()
                tilename = image_file[:-4]
                cls.tiledict[tilename] = image
    
    @staticmethod
    def set_camera_position(position):
        GameWindow.prev_position = GameWindow.position
        GameWindow.position = position
    
    
    def enable_alpha(self):
        pass
    
    def set_round_update(self, func, timer_value):
        self.round_timer = timer_value
    
    @staticmethod
    def set_update(func):
        GameWindow.update_handler = func
    
    def clear(self):
        self.screen.fill((55, 55, 55))
    
    def run_app(self):
        update_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(update_timer, int(self.round_timer*1000))
        while 1:
            for event in pygame.event.get():
                if event.type==QUIT:
                    self.on_close()
                    
                elif event.type == MOUSEBUTTONDOWN:
                    x,y = pygame.mouse.get_pos()
                    y = GameWindow.height - y
                    self.on_mouse_press(x,y, event.button, [])
                
                elif event.type == MOUSEBUTTONUP:
                    x,y = pygame.mouse.get_pos()
                    y = GameWindow.height - y
                    self.on_mouse_release(x,y, event.button, [])
                    
                elif event.type == MOUSEMOTION:
    
                    if event.buttons[0]:
                        but = 1
                    elif event.buttons[2]:
                        but = 3
                    else:
                        but = False
                    if but:
                        x,y = pygame.mouse.get_pos()
                        y = GameWindow.height - y
                        
                        self.on_mouse_drag(x,y,0,0,but, [])
                    
                    
                elif event.type==KEYDOWN:
                    self.on_key_press(event.key, [])
                    
                elif event.type==KEYUP:
                    self.on_key_release(event.key, [])
                    
                elif event.type==update_timer:
                    self.round_update(0)
                    
            self.update(0)
            
            self.on_draw()
            pygame.display.update()
        
    @staticmethod
    def draw_tile(tilename, x,y):
        image = GameWindow.tiledict[tilename]
        width, height = image.get_width(), image.get_height()
        y = GameWindow.height - y
        x = x - width/2
        y = y - height/2
        rect = Rect(x,y, width, height)
        GameWindow.screen.blit(image, rect)
        
        
    
    @staticmethod
    def draw_label(text, font_size, x,y):
        font_name = "Comic Sans MS"
        color = (255,255,255)
        font = pygame.font.SysFont(font_name, 20)
        label = font.render(text, 1, color)
        dx = GameWindow.tiledict['player'].get_width()/2
        dy = GameWindow.tiledict['player'].get_height()/2
        GameWindow.screen.blit(label, (x-dx, y))
    
    def draw_background(self, x,y):
        y = -y
        image = GameWindow.tiledict['grass_full']
        rect = Rect(x,y, image.get_width(), image.get_height())
        self.screen.blit(image, rect)


class GUIWindow:
    def __init__(self, height, width):
        pass


class Label(object):
    font_name = "Comic Sans MS"
    color = (255, 255, 255)
    def __init__(self, text, x,y):
        self.font = pygame.font.SysFont(self.font_name, 30)
        self.x, self.y = x,y
        self.x = GameWindow.width -x*1.8
        self._text = text
        self.label = self.font.render(text, 1, self.color )
    @property
    def text(self):
        return self._text
    @text.setter
    def text(self, text):
        self.label = self.font.render(text, 1, self.color )
    def draw(self):
        GameWindow.screen.blit(self.label, (self.x, self.y))
