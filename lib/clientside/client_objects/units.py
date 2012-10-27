#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from config import TILESIZE

from clientside.gui.window import create_tile, create_label
from share.mathlib import Point

from clientside.client_objects.objects_lib import *



    
class Player(Sweemer, Movable, DynamicObject, Deadly):
    tilename = 'player'
    move_frames = 2
    defend_frames = 1
    def __init__(self, name, position, hp, hp_value):
        DynamicObject.__init__(self, name, position)
        Movable.__init__(self, self.move_frames)
        
        Deadly.__init__(self, hp, hp_value, self.defend_frames)
    
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
        
    


class Self(Player):
    tilename = 'self'

class Ally(Player):
    tilename = 'ally'
    move_frames = 11
    defend_frames = 3

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




class Bat(MetaMonster):
    tilename = 'bat'
    move_frames = 10
    dead_frames = 3
    fight_frames =1
    def __init__(self, name, position, hp, hp_value):
        MetaMonster.__init__(self, name, position,
                    self.move_frames, self.dead_frames, self.fight_frames,
                    hp, hp_value)
                    

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

