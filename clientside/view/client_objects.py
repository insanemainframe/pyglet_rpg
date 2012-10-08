#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from config import TILESIZE

from clientside.gui.window import GameWindow, create_tile, create_label
from share.mathlib import Point, NullPoint

from clientside.view.objects_lib import DynamicObject, Animated, Movable, MapAccess

Meta = DynamicObject

class Fighter(Animated):
    def __init__(self, frames):
        Animated.__init__(self)
        self.create_animation('attack', 'attack', frames,3)
        self.attacking = False
    
    def attack(self):
        self.attacking = True
    
    def draw(self):
        tilename = self.tilename + self.get_animation('attack')
        return [create_tile(self.position, tilename)]
    
    def round_update(self):
        self.attacking = False
            
class Sweemer(MapAccess):
    def update(self, delta):
        i,j = (self.position/TILESIZE).get()
        if MapAccess.map[i][j]=='water':
            self.inwater= True
            self.prefix = '_water'
        else:
            self.inwater = False
            self.prefix = ''
    

class Deadly(Animated):
    def __init__(self, frames):
        Animated.__init__(self)
        self.dead = False
        self.defended = False
        self.create_animation('death', 'die', frames, 3)
        self.create_animation('defend', 'defend', 2, 3)
    
    def draw(self):
        position = self.position
        if self.dead:
            tilename = self.tilename + self.get_animation('death')
        else:
            tilename = self.tilename + self.get_animation('defend')
        return [create_tile(position, tilename, -1 )]
    
    def die(self):
        self.dead = True
    
    def defend(self):
        self.defended = True
    
    def round_update(self):
        self.defended = False

    
class Player(Sweemer, Movable, DynamicObject, Deadly):
    tilename = 'player'
    def __init__(self, name, position):
        DynamicObject.__init__(self, name, position)
        Movable.__init__(self, 2)
        
        Deadly.__init__(self, 1)
    
    def draw(self):
        if self.dead or self.defended:
            return Deadly.draw(self)
        else:
            tiles = Movable.draw(self)
            label  = create_label(self.name, self.position)
            return tiles + [label]
            
        
    def update(self, dt):
        Sweemer.update(self, dt)
        Movable.update(self, dt)
    

    def die(self):
        self.moving = False
        Deadly.die(self)
        
    


class Self(Player, Deadly, DynamicObject):
    tilename = 'self'


class Zombie(Movable, DynamicObject, Deadly, Fighter):
    tilename = 'zombie'
    def __init__(self, name, position):
        DynamicObject.__init__(self, name, position)
        Movable.__init__(self, 2)
        Deadly.__init__(self, 10)
        Fighter.__init__(self,1)
    
    def draw(self):
        if self.attacking:
            return Fighter.draw(self)
        elif not self.dead and not self.defended:
            return Movable.draw(self)
        else:
            return Deadly.draw(self)
    
    def round_update(self):
        Fighter.round_update(self)

class Cat(Movable, DynamicObject):
    tilename = 'cat'
    def __init__(self, name, position):
        DynamicObject.__init__(self, name, position)
        Movable.__init__(self, 5)
        self._rainbow = False
        self.create_animation('rainbow', 'rainbow', 3,2)
    
    def rainbow(self):
        self._rainbow = True
    
    def draw(self):
        if self._rainbow:
            tilename = self.tilename + self.get_animation('rainbow')
            return [create_tile(self.position, tilename, 1)]
        else:
            return Movable.draw(self)
    
    def round_update(self):
        self._rainbow = False
        Movable.round_update(self)
    


        
class Ghast(Movable, DynamicObject, Deadly, Fighter):
    tilename = 'ghast'
    def __init__(self, name, position):
        DynamicObject.__init__(self, name, position)
        Movable.__init__(self, 2)
        Deadly.__init__(self, 1)
        Fighter.__init__(self,3)
    

    def draw(self):
        if self.attacking:
            return Fighter.draw(self)
        elif not self.dead and not self.defended:
            return Movable.draw(self)
        else:
            return Deadly.draw(self)
    
    def round_update(self):
        Fighter.round_update(self)
        
class Lych(Movable, DynamicObject, Deadly):
    tilename = 'lych'
    def __init__(self, name, position):
        DynamicObject.__init__(self, name, position)
        Movable.__init__(self)
        Deadly.__init__(self, 1)
    
    def draw(self):
        if not self.dead and not self.defended:
            return Movable.draw(self)
        else:
            return Deadly.draw(self)
    
    
    

class Ball(Movable, DynamicObject, Animated):
    tilename = 'ball'
    def __init__(self, name, position):
        DynamicObject.__init__(self, name, position)
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
        self.explosion = True
        self.moving = False

class DarkBall(Ball):
    tilename = 'darkball'
    explode_tile = 'darkball_explode'

class SkillBall(Ball):
    tilename = 'skillball'
    explode_tile = 'skillball_explode'
    
