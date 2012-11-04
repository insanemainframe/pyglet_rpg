#!/usr/bin/env python
# -*- coding: utf-8 -*-
from engine.enginelib.meta import *
from engine.gameobjects.shells import SkillBall

class Skill:
    def __init__(self, number=5):
        self.skills = number
        self.directs = (Point(1,0), Point(-1,0), Point(0,-1), Point(0,1),
                        Point(1,1), Point(1,-1), Point(-1,1), Point(-1,-1),
                        Point(2,1), Point(2,-1), Point(-2,1), Point(-2,-1),
                        Point(1,2), Point(1,-2), Point(-1,2), Point(-1,-2))
    
    def skill(self):
        if self.skills>0:
            for direct in self.directs:
                ball = SkillBall(direct, self.fraction, proxy(self), self.damage)
                self.location.new_object(ball, position = self.position)
            self.skills-=1
    
    def plus_skill(self):
        self.skills+=1

