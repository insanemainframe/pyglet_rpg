#!/usr/bin/env python
# -*- coding: utf-8 -*-
from engine.mathlib import Cord, Position, ChunkCord

from engine.enginelib.meta import *
from engine.gameobjects.shells import SkillBall


class Skillable(object):
    def mixin(self):
        self.__slots = {}

    def add_skill(self, skill_type):
        assert issubclass(skill_type, SkillABC)
        if skill_type not in self.__slots:
            self.a

    def set_skill(self, ):
        pass
    def apply_skill(self):
        pass


class SkillABC(object):
    pass


class Skill(SkillABC):
    __impulse = 60
    def mixin(self, number=5):
        self.skills = number
        self.directs = (Position(1,0), Position(-1,0), Position(0,-1), Position(0,1),
                        Position(1,1), Position(1,-1), Position(-1,1), Position(-1,-1),
                        Position(2,1), Position(2,-1), Position(-2,1), Position(-2,-1),
                        Position(1,2), Position(1,-2), Position(-1,2), Position(-1,-2))
    
    def skill(self):
        if self.skills>0:
            for direct in self.directs:
                ball = SkillBall(direct, self.__impulse, proxy(self))

                self.location.new_object(ball, position = self.position)
            self.skills-=1
    
    def plus_skill(self):
        self.skills+=1

