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
    
    def create_animation(self, name, tilename, frames, freq, repeat = True):
        self.animations[name] = {}
        self.animations[name]['counter'] = 0
        self.animations[name]['tilename'] = tilename
        self.animations[name]['frames'] = frames
        self.animations[name]['freq'] = freq
        self.animations[name]['frame_counter'] = freq
        self.animations[name]['delay'] = freq*frames
        self.animations[name]['repeat?'] = repeat
        
        
    
    def get_animation(self, name):
        freq = self.animations[name]['freq']
        if self.animations[name]['frame_counter']<freq:
            self.animations[name]['frame_counter']+=1
        else:
            self.animations[name]['frame_counter'] = 0
            frames = self.animations[name]['frames']
            if self.animations[name]['counter']< frames:
                self.animations[name]['counter']+=1
            else:
                if not self.animations[name]['repeat?']:
                    self.REMOVE = True
                self.animations[name]['counter'] = 0
            
        tilename = self.animations[name]['tilename']
        n = self.animations[name]['counter']
        tilename = '_'+tilename+'_%s' % n
        return tilename
    
#
class Movable(Animated):
    def __init__(self, frames=1):
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
        else:
            self.moving = False
    
    def round_update(self):
        self.moving = False
    
    def force_complete(self):
        if self.vector:
            self.position+=self.vector
            self.vector = NullPoint


class Deadly(Animated):
    def __init__(self, frames):
        self.frames = frames
    
    def die(self):
        self.create_animation('dying', 'die', self.frames, 3)
        
        
            
class Sweemer:
    def update(self, delta):
        i,j = (self.position/TILESIZE).get()
        if Sweemer.map[i][j]=='water':
            self.inwater= True
            self.prefix = '_water'
        else:
            self.inwater = False
            self.prefix = ''
    

class Deadly:
    def __init__(self, frames):
        self.dead = False
        self.create_animation('death', 'die', frames, 3)
    
    def draw(self):
        position = self.position
        tilename = self.tilename + self.get_animation('death')
        return [create_tile(position, tilename )]
    
    def die(self):
        self.dead = True
        
    
class Player(Sweemer, Movable, Object, Deadly):
    tilename = 'player'
    def __init__(self, name, position):
        Object.__init__(self, name, position)
        Movable.__init__(self)
        Deadly.__init__(self, 0)
    
    def draw(self):
        tiles = Movable.draw(self)
        label  = create_label(self.name, self.position)
        return tiles + [label]
        
    def update(self, dt):
        Sweemer.update(self, dt)
        Movable.update(self, dt)
    

    def die(self):
        self.tilename = 'player_die'
        self.moving = False
        
    


class SelfPlayer(Player, Deadly):
    tilename = 'self'
    def update(self, dt):
        Sweemer.update(self, dt)
        Player.update(self, dt)

class Zombie(Movable, Object, Deadly):
    tilename = 'zombie'
    def __init__(self, name, position):
        Object.__init__(self, name, position)
        Movable.__init__(self)
        Deadly.__init__(self, 9)
    
    def draw(self):
        if not self.dead:
            return Movable.draw(self)
        else:
            return Deadly.draw(self)
    


        
class Ghast(Movable, Object, Deadly):
    tilename = 'ghast'
    def __init__(self, name, position):
        Object.__init__(self, name, position)
        Movable.__init__(self, 2)
        Deadly.__init__(self, 1)
        
class Lych(Movable, Object, Deadly):
    tilename = 'lych'
    def __init__(self, name, position):
        Object.__init__(self, name, position)
        Movable.__init__(self)
        Deadly.__init__(self, 1)
    

class Ball(Movable, Object, Animated):
    tilename = 'ball'
    def __init__(self, name, position):
        Object.__init__(self, name, position)
        Movable.__init__(self)
        self.create_animation('explosion', 'explode', 7,3)
        self.explosion = False
        
    def update(self, dt):
        if not self.explosion:
            return Movable.update(self, dt)
    
    def draw(self):
        if not self.explosion:
            return Movable.draw(self)
        else:
            tilename = self.tilename + self.get_animation('explosion')
            return [create_tile(self.position, tilename, 1)]
    
    def explode(self):
        print 'explode'
        self.explosion = True
        self.moving = False

class DarkBall(Ball):
    tilename = 'darkball'
    explode_tile = 'darkball_explode'
   

object_dict = {'Player' : Player, 'Ball': Ball, 'self': SelfPlayer,
            'Zombie':Zombie, 'DarkBall':DarkBall, 'Lych':Lych, 'Ghast' : Ghast}
