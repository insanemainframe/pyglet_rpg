#!/usr/bin/env python
# -*- coding: utf-8 -*-
from engine.mathlib import Cord, Position, ChunkCord

from engine.enginelib.meta import *
from engine.gameobjects.shells import SkillBall

class Skill:
    def mixin(self, number=5):
        self.skills = number
        self.directs = (Position(1,0), Position(-1,0), Position(0,-1), Position(0,1),
                        Position(1,1), Position(1,-1), Position(-1,1), Position(-1,-1),
                        Position(2,1), Position(2,-1), Position(-2,1), Position(-2,-1),
                        Position(1,2), Position(1,-2), Position(-1,2), Position(-1,-2))
    
    def skill(self):
        if self.skills>0:
            for direct in self.directs:
                ball = SkillBall(direct, self.fraction, proxy(self), self.damage)
                self.location.new_object(ball, position = self.position)
            self.skills-=1
    
    def plus_skill(self):
        self.skills+=1

