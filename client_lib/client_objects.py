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
        print 'create %s' % name
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
            
            
    def draw(self, shift):
        position = self.position - shift - Point(TILESIZE/2,TILESIZE/2)
        if self.moving:
            if self.animation>0:
                tilename = self.tilename+'_move'
            else:
                tilename = self.tilename+'_move_'
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
    
class Player(Movable, Object):
    tilename = 'player'
    def __init__(self, name, position):
        Object.__init__(self, name, position)
        Movable.__init__(self)
    
    def draw(self, shift):
        tile = Movable.draw(self,shift)
        label  = create_label(self.name, Point(*tile[0][1]))
        return tile + [label]
    
    def die(self):
        self.tilename = 'player_die'
        self.DELAY = 5
        self.REMOVE = True
        self.moving = False
        
    


class SelfPlayer(Player):
    tilename = 'self'


class Ball(Movable, Object):
    tilename = 'ball'
    def __init__(self, name, position):
        Object.__init__(self, name, position)
        Movable.__init__(self)
    
    def update(self, delta):
        if self.REMOVE:
            self.explode_c+=1
            self.tilename = 'ball_explode_%s' % self.explode_c
        else:
            Movable.update(self, delta)
    
    def explode(self):
        self.explode_c = 1
        self.tilename = 'ball_explode_%s' % self.explode_c
        self.DELAY = 5
        self.REMOVE = True
        self.moving = False
        print 'ball explosion'
    
   

object_dict = {'Player' : Player, 'Ball': Ball, 'self': SelfPlayer}
