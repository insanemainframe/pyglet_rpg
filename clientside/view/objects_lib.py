#!/usr/bin/env python
# -*- coding: utf-8 -*-
from clientside.gui.window import GameWindow, create_tile, create_label

from share.mathlib import Point, NullPoint

from inspect import getmro

class ActionError(Exception):
    pass

class StaticObject:
    def __init__(self, name, position):
        self.name = name
        self.position = position
        self.REMOVE = False
        self.hovered = False
    
    def handle_action(self, action, args):
        if hasattr(self, action):
            getattr(self, action)(*args)
        else:
            raise ActionError('no action %s.%s' % (self.__class__.__name__, action))
    def hover(self):
        self.hovered = True
    
    def draw(self):
        if self.hovered:
            tilename = self.tilename + '_hover'
        else:
            tilename = self.tilename
        return [create_tile(self.position, tilename, -1)]
    
    def remove(self):
        self.REMOVE = True

class ClientObject:
    REMOVE = False
    "класс игрового объекта на карте"
    def __init__(self, name, position):
        self.position = position
        self.name = name
        
    def handle_action(self, action, args):
        if hasattr(self, action):
            getattr(self, action)(*args)
        else:
            raise ActionError('no action %s.%s' % (self.__class__.__name__, action))
            
    def draw(self):
        return [create_tile( self.position, self.tilename)]
        
    def update(self, delta):
        pass
    
    def force_complete(self):
        pass
        
    def round_update(self):
        bases = getmro(self.__class__)
        for base in bases:
            if not base is object and not base is ClientObject and hasattr(base, 'round_update'):
                    base.round_update(self)
    
    def exist(self, *args):
        pass
    
    
    def remove(self):
        self.REMOVE = True


class MapAccess:
    pass

########################################################################
class Animated:
    "класс для анимированных объектов"
    def __init__(self):
        if not hasattr(self, 'init'):
            self.init = True
            self.animations = {}
        
    def create_animation(self, name, tilename, frames, freq, repeat = True):
        frames-=1
        self.animations[name] = {}
        self.animations[name]['counter'] = 0
        self.animations[name]['tilename'] = tilename
        self.animations[name]['frames'] = frames #количество кадров на анимацию
        self.animations[name]['freq'] = freq #количество кадров на каждый кадр анимации
        self.animations[name]['frame_counter'] = 0 #счетчик фреймов текущего кадра 
        self.animations[name]['repeat?'] = repeat
        self.animations[name]['repeated'] = False
        self.animations[name]['prev_frame'] = 0
        
        
    
    def get_animation(self, name):
        freq = self.animations[name]['freq']
        tilename = self.animations[name]['tilename']
        repeated = self.animations[name]['repeated']
        need_repeat = self.animations[name]['repeat?']
        prev_frame = self.animations[name]['prev_frame']
        
        if repeated and not need_repeat:
            n = self.animations[name]['frames']
        else:
            if self.animations[name]['frame_counter']<freq:
                self.animations[name]['frame_counter']+=1
            else:
                self.animations[name]['frame_counter'] = 0
                frames = self.animations[name]['frames']
                if self.animations[name]['counter'] < frames-1:
                    self.animations[name]['counter']+=1
                else:
                    if not self.animations[name]['repeat?']:
                        self.animations[name]['repeated'] = True
                    self.animations[name]['counter'] = 0
            
            n = self.animations[name]['counter']
            
            
        tilename = '_'+tilename+'_%s' % n

        return tilename
    
#
class Movable(Animated, ClientObject):
    def __init__(self, frames=1):
        Animated.__init__(self)
        self.moving = False
        self.vector = NullPoint
        self.create_animation('moving', 'move', frames,2)
    
    def move(self, xy):
        vector = Point(*xy)
        self.vector += vector
        if self.vector:
            self.moving = True
            
            
    def draw(self):
        position = self.position
        if self.moving:
            tilename = self.tilename + self.get_animation('moving')
        else:
            tilename = self.tilename
        return [create_tile(position, tilename)]

    def update(self, delta):
        if self.vector:
            move_vector = self.vector * delta
            if move_vector>self.vector:
                move_vector = self.vector
            self.position += move_vector
            self.vector -=move_vector
        else:
            self.moving = False
    
    def round_update(self):
        self.moving = False
    
    def force_complete(self):
        if self.vector:
            self.position+=self.vector
            self.vector = NullPoint
