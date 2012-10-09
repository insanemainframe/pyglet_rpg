#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from config import TILESIZE

from clientside.gui.window import create_tile, create_label
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
    def __init__(self, hp_value, hp,frames):
        Animated.__init__(self)
        self.dead = False
        self.defended = False
        
        self.hp = hp
        self.hp_value = hp_value
        
        self.create_animation('death', 'die', frames, 3)
        self.create_animation('defend', 'defend', 2, 3)
    
    def change_hp(self, hp_value, hp):
        self.hp = hp
        self.hp_value = hp_value
    
    def draw(self):
        position = self.position
        if self.dead:
            tilename = self.tilename + self.get_animation('death')
        else:
            tilename = self.tilename + self.get_animation('defend')
        
        sprite = create_tile(position, tilename, -1 )
        return [sprite]
    
    def draw_label(self):
        label = create_label('%d/%d' % (self.hp, self.hp_value), self.position+Point(0, self.sprite.height))
        return [label]
    
    def die(self):
        self.dead = True
    
    def defend(self):
        self.defended = True
    
    def round_update(self):
        self.defended = False

    
class Player(Sweemer, Movable, DynamicObject, Deadly):
    tilename = 'player'
    def __init__(self, name, position, hp, hp_value):
        DynamicObject.__init__(self, name, position)
        Movable.__init__(self, 2)
        
        Deadly.__init__(self, hp, hp_value, 1)
    
    def draw(self):
        if self.dead or self.defended:
            sprite =  Deadly.draw(self) 
        else:
            tiles = Movable.draw(self)
            label  = create_label(self.name, self.position)
            sprite =  tiles + [label]
        
        return sprite + Deadly.draw_label(self)
            
        
    def update(self, dt):
        Sweemer.update(self, dt)
        Movable.update(self, dt)
    

    def die(self):
        self.moving = False
        Deadly.die(self)
    
    def round_update(self):
        Deadly.round_update(self)
        Movable.round_update(self)
        
    


class Self(Player, Deadly, DynamicObject):
    tilename = 'self'


class MetaMonster(Movable, DynamicObject, Deadly, Fighter):
    def __init__(self, name, position, move_frames, dead_frames, fight_frames,hp, hp_value):
        DynamicObject.__init__(self, name, position)
        Movable.__init__(self, move_frames)
        Deadly.__init__(self, hp, hp_value, dead_frames)
        Fighter.__init__(self,fight_frames)
    
    def draw(self):
        if self.attacking:
            sprite =  Fighter.draw(self)
        elif not self.dead and not self.defended:
            sprite =  Movable.draw(self)
        elif self.dead:
            return Deadly.draw(self)
        else:
            sprite =  Deadly.draw(self)
        
        return sprite + Deadly.draw_label(self)
    
    def round_update(self):
        Fighter.round_update(self)
        Deadly.round_update(self)

class Zombie(MetaMonster):
    tilename = 'zombie'
    move_frames = 2
    dead_frames = 10
    fight_frames =1
    def __init__(self, name, position, hp, hp_value):
        MetaMonster.__init__(self, name, position,
                    self.move_frames, self.dead_frames, self.fight_frames,
                    hp, hp_value)
    
    


    


        
class Ghast(MetaMonster):
    tilename = 'ghast'
    move_frames = 2
    dead_frames = 1
    fight_frames = 3
    def __init__(self, name, position, hp, hp_value):
        MetaMonster.__init__(self, name, position,
                    self.move_frames, self.dead_frames, self.fight_frames,
                    hp, hp_value)
    
     
    
        
class Lych(MetaMonster):
    tilename = 'lych'
    move_frames = 1
    dead_frames = 1
    fight_frames = 1
    def __init__(self, name, position, hp, hp_value):
        MetaMonster.__init__(self, name, position,
                    self.move_frames, self.dead_frames, self.fight_frames,
                    hp, hp_value)
     
    
    
    
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
    
