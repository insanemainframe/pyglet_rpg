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
        #print 'create %s' % name
        self.position = position
        self.name = name
    
    def handle_action(self, action, args):
        if hasattr(self, action):
            #print 'handle %s %s' % (action, str(args))
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

class Movable:
    def __init__(self):
        self.moving = False
        self.animation = 1
        self.vector = NullPoint
        
    
    def move(self, xy):
        vector = Point(*xy)
        self.vector += vector
        if self.vector:
            self.moving = True
            
            
    def draw(self, shift, prefix=''):
        position = self.position - shift - Point(TILESIZE/2,TILESIZE/2)
        if self.moving:
            if self.animation>0:
                tilename = self.tilename+'_move' + prefix
            else:
                tilename = self.tilename+'_move_'+ prefix
            self.animation*=-1
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
            print 'force move %s for %s' % (self.name, self.vector)
            self.position+=self.vector
            self.vector = NullPoint

from math import ceil
class Animated:
    def __init__(self, tilename, frames, freq=1):
        self.frames = frames
        self.freq = float(freq)
        self.animation_counter = 1
        self.animation_tilename = tilename
        self.DELAY = frames * freq
    
    def draw(self, shift):
        position = self.position - shift - Point(TILESIZE/2,TILESIZE/2)
        n = int(ceil(self.animation_counter/self.freq))
        tilename = self.animation_tilename+'_%s' % n
        
        
        return [create_tile(position, tilename)]
    
    def update(self, delta):
        if self.animation_counter==self.frames*self.freq:
            print 'clear counter'
            self.DELAY = 0
        else:
            self.animation_counter+=1
        
        
            
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
    
    def draw(self, shift, prefix=[]):
        tiles = Movable.draw(self,shift, self.prefix)
        label  = create_label(self.name, Point(*tiles[0][1]))
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


class Ball(Movable, Object, Animated):
    tilename = 'ball'
    def __init__(self, name, position):
        Object.__init__(self, name, position)
        Movable.__init__(self)
        
    def update(self, dt):
        if not self.REMOVE:
            return Movable.update(self, dt)
        else:
            return Animated.update(self, dt)
    
    def draw(self, shift):
        if not self.REMOVE:
            return Movable.draw(self, shift)
        else:
            return Animated.draw(self, shift)
    
    def explode(self):
        Animated.__init__(self, 'ball_explode',7,3)
        self.REMOVE = True
        self.moving = False
    
   

object_dict = {'Player' : Player, 'Ball': Ball, 'self': SelfPlayer}
