#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import path
path.append('../')

from pyglet.window.key import UP, DOWN, LEFT, RIGHT, RSHIFT
from pyglet.image.codecs.png import PNGImageDecoder

import pyglet
from pyglet.gl import *

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

########################################################################
class GameWindow:
    "разделяемое состояние элементов gui"
    def __init__(self, width, height):
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
        cls.gentiles()
        
    @staticmethod
    def gentiles():
        cls = GameWindow
        cls.unknown = pyglet.image.load(join(TILESDIR, 'unknown.png'), decoder=PNGImageDecoder()).get_texture()
        
        cls.tiledict = defaultdict(lambda: cls.unknown)
        for root, subfolders, files in walk(TILESDIR):
            for image_file in files:
                image = pyglet.image.load(join(root,image_file), decoder=PNGImageDecoder()).get_texture()
                tilename = image_file[:-4]
                cls.tiledict[tilename] = image
    
    @staticmethod
    def set_camera_position(position):
        GameWindow.prev_position = GameWindow.position
        GameWindow.position = position
    
    def enable_alpha(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        

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
class InputHandle:
    "перехват устройств ввода"
    pressed = {}
    MOVE_BUTTON = 1
    STRIKE_BUTTON = 4
    control_keys = [UP, DOWN, LEFT, RIGHT, RSHIFT]
    striking = False
    
    def __init__(self):
        self.step = TILESIZE/2
        self.vector = NullPoint
        self.vectors = {UP:Point(0,self.step), DOWN: Point(0,-self.step),
               LEFT : Point(-self.step,0), RIGHT : Point(self.step,0)}
            
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
        if button==self.MOVE_BUTTON:
            self.vector = (Point(x,y) - self.center)
            
            
        elif button==self.STRIKE_BUTTON:
            vector = (Point(x,y) - self.center)
            self.send_ball(vector)
            self.striking = vector
    
    def on_mouse_release(self, x, y, button, modifiers):
        if button==self.MOVE_BUTTON:
            self.vector = False
        elif button==self.STRIKE_BUTTON:
            self.striking = False
    
    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if button==self.MOVE_BUTTON:
            self.vector = (Point(x,y) - self.center)
        elif button==self.STRIKE_BUTTON:
            self.striking = (Point(x,y) - self.center)
            
        
    
    def handle_input(self):
        self.step = self.stats.speed
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
                self.send_move(vector)
        elif self.vector:
            self.send_move(self.vector)
        if self.striking:
            self.send_ball(self.striking)
            

class Drawable(GameWindow):
    "рисуемые объекты"
    def __init__(self):
        self.animation = 1
        self.animation_counter = 0
        self.aps = 15
    
    def draw(self):
        self.tiles.sort(lambda x,y: -1 if x[0]>y[0] else 1)
        
        for layer,tilename, position, sptite_type in self.tiles:
            if sptite_type=='tile':
                width = self.tiledict[tilename].width
                height = self.tiledict[tilename].height
                shift =  Point(width/2, height/2)
                x,y = (position-shift).get()
                if -TILESIZE<x<self.width and -TILESIZE<x<self.height:
                    self.tiledict[tilename].blit(x,y, width=width, height=height)
                    
            elif sptite_type=='label':
                shift = self.center
                x,y = (position-shift).get()
                pyglet.text.Label(tilename,
                          font_name='Times New Roman',
                          font_size=10,
                          x=x, y=y,
                          anchor_x='center', anchor_y='center').draw()
                

class Stats(GameWindow):
    hp = 0
    hp_value = 0
    kills = 0
    speed = 0
    deaths = 0
    damage = 0
    gold = 0
    def __init__(self):

        
        hp_mess = 'hp: %s/%s' % (self.hp, self.hp_value)
        self.hp_display = self.label(hp_mess, 70, 20)
                          
        kills_mess = 'kills: %s' % self.kills
        self.kills_display = self.label(kills_mess, 70, 40)
                          
        deaths_mess = 'deaths: %s' % self.deaths
        self.deaths_display = self.label(deaths_mess, 70, 60)
        
        gold_mess = 'gold %s' % self.gold
        self.gold_display = self.label(gold_mess, 70, 80)
        
        speed_mess = 'speed: %s' % self.speed
        self.speed_display = self.label(speed_mess, 70, 100)
        
        damage_mess = 'damage: %s' % self.damage
        self.damage_display = self.label(damage_mess, 70, 120)
        
        
    def label(self, text, x,y):
        return pyglet.text.Label(text,
                          font_name='Times New Roman',
                          font_size=20,
                          x=self.width-x, y=self.height-y,
                          anchor_x='center', anchor_y='center')
                          
    def update(self, hp, hp_value, speed, damage, gold, kills, deaths):
        self.hp = hp
        self.hp_value = hp_value
        self.deaths = deaths
        self.kills = kills
        self.gold = gold
        self.speed = speed
        self.damage = damage
        
        self.speed_display.text = 'speed: %s' % self.speed
        self.damage_display.text = 'damage: %s' % self.damage
        self.hp_display.text = 'hp: %s/%s' % (self.hp, self.hp_value)
        self.kills_display.text = 'kills: %s' % self.kills
        self.deaths_display.text = 'deaths: %s' % self.deaths
        self.gold_display.text = 'gold: %s' % self.gold
        
    def draw(self):
        self.hp_display.draw()
        self.kills_display.draw()
        self.deaths_display.draw()
        self.gold_display.draw()
        self.speed_display.draw()
        self.damage_display.draw()
