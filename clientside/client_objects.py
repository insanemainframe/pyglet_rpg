#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from sys import path
path.append('../')

from gui_lib import create_tile, create_label

from share.mathlib import Point, NullPoint

from config import TILESIZE

class ActionError(Exception):
    pass

class ClientObject:
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
            raise ActionError('no action %s.%s' % (self.__class__.__name__, action))
            
    def draw(self):
        return [create_tile( self.position, self.tilename)]
        
    def update(self, delta):
        pass
    
    def force_complete(self):
        pass
        
    def round_update(self):
        pass
    
    def exist(self, *args):
        pass

    
    def remove(self):
        self.REMOVE = True
    
########################################################################
from math import ceil
class Animated:
    animations = {}
    
    def create_animation(self, name, tilename, frames, freq, repeat = True):
        frames-=1
        self.animations[name] = {}
        self.animations[name]['counter'] = 0
        self.animations[name]['tilename'] = tilename
        self.animations[name]['frames'] = frames
        self.animations[name]['freq'] = freq
        self.animations[name]['frame_counter'] = freq
        self.animations[name]['delay'] = freq*frames
        self.animations[name]['repeat?'] = repeat
        self.animations[name]['repeated'] = False
        self.animations[name]['prev_frame'] = 0
        
        
    
    def get_animation(self, name):
        freq = self.animations[name]['freq']
        tilename = self.animations[name]['tilename']
        repeated = self.animations[name]['repeated']
        need_repeat = self.animations[name]['repeat?']
        prev_frame = self.animations[name]['prev_frame']
        
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
            
        if repeated and not need_repeat:
            n = prev_frame
        else:
            n = self.animations[name]['counter']
            self.animations[name]['prev_frame'] = n
        tilename = '_'+tilename+'_%s' % n
        print tilename
        return tilename
    
#
class Movable(Animated, ClientObject):
    def __init__(self, frames=1):
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


        
        
            
class Sweemer:
    def update(self, delta):
        i,j = (self.position/TILESIZE).get()
        if Sweemer.map[i][j]=='water':
            self.inwater= True
            self.prefix = '_water'
        else:
            self.inwater = False
            self.prefix = ''
    

class Deadly(Animated):
    def __init__(self, frames):
        self.dead = False
        self.create_animation('death', 'die', frames, 3)
    
    def draw(self):
        position = self.position
        tilename = self.tilename + self.get_animation('death')
        return [create_tile(position, tilename, -1 )]
    
    def die(self):
        self.dead = True
        
    
class Player(Sweemer, Movable, ClientObject, Deadly):
    tilename = 'player'
    def __init__(self, name, position):
        ClientObject.__init__(self, name, position)
        Movable.__init__(self, 2)
        Deadly.__init__(self, 1)
    
    def draw(self):
        if not self.dead:
            tiles = Movable.draw(self)
            label  = create_label(self.name, self.position)
            return tiles + [label]
        else:
            return Deadly.draw(self)
        
    def update(self, dt):
        Sweemer.update(self, dt)
        Movable.update(self, dt)
    

    def die(self):
        self.moving = False
        Deadly.die(self)
        
    


class Self(Player, Deadly, ClientObject):
    tilename = 'self'


class Zombie(Movable, ClientObject, Deadly):
    tilename = 'zombie'
    def __init__(self, name, position):
        ClientObject.__init__(self, name, position)
        Movable.__init__(self)
        Deadly.__init__(self, 10)
    
    def draw(self):
        if not self.dead:
            return Movable.draw(self)
        else:
            return Deadly.draw(self)
    


        
class Ghast(Movable, ClientObject, Deadly):
    tilename = 'ghast'
    def __init__(self, name, position):
        ClientObject.__init__(self, name, position)
        Movable.__init__(self, 2)
        Deadly.__init__(self, 1)
    def draw(self):
        if not self.dead:
            return Movable.draw(self)
        else:
            return Deadly.draw(self)
        
class Lych(Movable, ClientObject, Deadly):
    tilename = 'lych'
    def __init__(self, name, position):
        ClientObject.__init__(self, name, position)
        Movable.__init__(self)
        Deadly.__init__(self, 1)
    
    def draw(self):
        if not self.dead:
            return Movable.draw(self)
        else:
            return Deadly.draw(self)
    

class Ball(Movable, ClientObject, Animated):
    tilename = 'ball'
    def __init__(self, name, position):
        ClientObject.__init__(self, name, position)
        Movable.__init__(self)
        self.create_animation('explosion', 'explode', 7,3, False)
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

class Corpse(ClientObject):
    tilename = 'corpse'

class Item(ClientObject):
    pass
    
class HealPotion(Item):
    tilename = 'heal_potion'

class SpeedPotion(Item):
    tilename = 'speed_potion'

class Sword(Item):
    tilename = 'sword'

class Gold(Item):
    tilename = 'gold'

class Armor(Item):
    tilename = 'armor'

class Sceptre(Item):
    tilename = 'sceptre'
