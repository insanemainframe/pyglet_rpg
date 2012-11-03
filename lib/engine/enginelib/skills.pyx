#!/usr/bin/env python
# -*- coding: utf-8 -*-
from engine.gameobjects.shells import SkillBall

from share.point cimport Point


class Skill:
    directs = (Point(1,0), Point(-1,0), Point(0,-1), Point(0,1),
                        Point(1,1), Point(1,-1), Point(-1,1), Point(-1,-1),
                        Point(2,1), Point(2,-1), Point(-2,1), Point(-2,-1),
                        Point(1,2), Point(1,-2), Point(-1,2), Point(-1,-2))

    def __init__(self, int number=5):
        self.skills = number
    
    def skill(self):
        cdef Point direct
        
        if self.skills>0:
            for direct in self.directs:
                ball = SkillBall(self.position, direct, self.fraction, self.name, self.damage)
                self.location.new_object(ball)
            self.skills-=1
    
    def plus_skill(self):
        self.skills+=1

