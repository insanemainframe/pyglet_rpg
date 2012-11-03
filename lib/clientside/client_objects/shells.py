#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import TILESIZE

from clientside.gui.window import create_tile, create_label
from share.point import Point

from clientside.client_objects.objects_lib import DynamicObject, Animated, Movable, MapAccess


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
        else:
            if self.explode_time>0:
                self.explode_time-=1
            else:
                self._REMOVE = True

    
    def draw(self):
        if not self.explosion:
            return Movable.draw(self)
        else:
            tilename = self.tilename + self.get_animation('explosion')
            return [create_tile(self.position, tilename, 1)]
    
    def explode(self, explode_time):
        self.explosion = True
        self.explode_time = explode_time
        self.moving = False

class DarkBall(Ball):
    tilename = 'darkball'
    explode_tile = 'darkball_explode'

class AllyBall(Ball):
    tilename = 'ally_ball'
    explode_tile = 'ally_ball_explode'

class SkillBall(Ball):
    tilename = 'skillball'
    explode_tile = 'skillball_explode'
    
