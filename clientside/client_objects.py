#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from sys import path
path.append('../')

from gui_lib import create_tile, create_label

from game_lib.math_lib import Point, NullPoint

from config import TILESIZE

class ActionError(Exception):
    pass

class Object:
    REMOVE = False
    DELAY = 0
    "класс игрового объекта на карте"
    def __init__(self, name, position):
        self.position = position
        self.name = name
        
    def handle_action(self, action, args):
        if hasattr(self, action):
            getattr(self, action)(*args)
        else:
            raise ActionError('no action %s' % action)
    def update(self, delta):
        pass
    
    def round_update(self):
        pass
    
    def remove(self):
        self.REMOVE = True
    
########################################################################
from math import ceil
class Animated:
    animations = {}
    
    def create_animation(self, name, tilename, frames, freq):
        self.animations[name] = {}
        self.animations[name]['counter'] = 0
        self.animations[name]['tilename'] = tilename
        self.animations[name]['frames'] = frames
        self.animations[name]['freq'] = freq
        self.animations[name]['delay'] = freq*frames
        
        
    
    def get_animation(self, name):
        counter = self.animations[name]['counter']
        freq = self.animations[name]['freq']
        tilename = self.animations[name]['tilename']
        n = int(counter/freq)
        tilename = '_'+tilename+'_%s' % n
        print 'get_animation', tilename
        return tilename
    
    def update_animation(self, name):
        counter = self.animations[name]['counter']
        freq = self.animations[name]['freq']
        frames = self.animations[name]['frames']
        if counter==frames*freq:
            print 'update_animtion CLEAR', counter, freq, frames
            self.animations[name]['delay'] = 0
        else:
            self.animations[name]['counter'] +=1
            print 'update_animtion', self.animations[name]['counter']
#
class Movable(Animated):
    def __init__(self):
        self.moving = False
        self.vector = NullPoint
        self.create_animation('moving', 'move', 1,2)
    
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
            self.update_animation('moving')
        else:
            self.moving = False
    
    def round_update(self):
        self.moving = False
    
    def force_complete(self):
        if self.vector:
            self.position+=self.vector
            self.vector = NullPoint


        
        
            
class Sweemer:
    def update(self, delta):
        i,j = (self.position/TILESIZE).get()
        if Sweemer.map[i][j]=='water':
            self.inwater= True
            self.prefix = '_water'
        else:
            self.inwater = False
            self.prefix = ''
    

        
        
    
class Player(Sweemer, Movable, Object):
    tilename = 'player'
    def __init__(self, name, position):
        Object.__init__(self, name, position)
        Movable.__init__(self)
    
    def draw(self):
        tiles = Movable.draw(self)
        label  = create_label(self.name, self.position)
        return tiles + [label]
        
    def update(self, dt):
        Sweemer.update(self, dt)
        Movable.update(self, dt)
    

    def die(self):
        self.tilename = 'player_die'
        self.DELAY = 5
        self.REMOVE = True
        self.moving = False
        
    


class SelfPlayer(Player):
    tilename = 'self'
    def update(self, dt):
        Sweemer.update(self, dt)
        Player.update(self, dt)

class Zombie(Movable, Object):
    tilename = 'zombie'
    def __init__(self, name, position):
        Object.__init__(self, name, position)
        Movable.__init__(self)
        
class Ghast(Movable, Object):
    tilename = 'ghast'
    def __init__(self, name, position):
        Object.__init__(self, name, position)
        Movable.__init__(self)
        
class Lych(Movable, Object):
    tilename = 'lych'
    def __init__(self, name, position):
        Object.__init__(self, name, position)
        Movable.__init__(self)
    

class Ball(Movable, Object, Animated):
    tilename = 'ball'
    def __init__(self, name, position):
        Object.__init__(self, name, position)
        Movable.__init__(self)
        self.create_animation('explosion', 'explode', 7,3)
        self.DELAY = 7*3
        
    def update(self, dt):
        if not self.REMOVE:
            return Movable.update(self, dt)
        else:
            return self.update_animation('explosion')
    
    def draw(self):
        if not self.REMOVE:
            return Movable.draw(self)
        else:
            tilename = self.tilename + self.get_animation('explosion')
            return [create_tile(self.position, tilename, 1)]
    
    def explode(self):
        
        self.REMOVE = True
        self.moving = False

class DarkBall(Ball):
    tilename = 'darkball'
    explode_tile = 'darkball_explode'
   

object_dict = {'Player' : Player, 'Ball': Ball, 'self': SelfPlayer,
            'Zombie':Zombie, 'DarkBall':DarkBall, 'Lych':Lych, 'Ghast' : Ghast}
