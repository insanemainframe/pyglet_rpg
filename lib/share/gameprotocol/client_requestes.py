#!/usr/bin/env python
# -*- coding: utf-8 -*-

from share.gameprotocol.meta import GameProtocol
from share.mathlib import Point



#передвижение
class Move(GameProtocol):
    def __init__(self, vector, destination):
        self.vector = vector
        self.destination = destination
    
    def pack(self):
        return self.vector.get(), self.destination
    
    @classmethod
    def unpack(cls, x_y, destination):
        x,y = x_y
        return (Point(x,y), destination)

#стрельба
class Strike(GameProtocol):
    def __init__(self, vector):
        self.vector = vector
    
    def pack(self):
        return self.vector.get()
    
    @classmethod
    def unpack(cls, x,y):
        return [Point(x,y)]


class ApplyItem(GameProtocol):
    def __init__(self, item_type):
        self.item_type = item_type
    
    def pack(self):
        return [self.item_type]
    
    @classmethod
    def unpack(cls, item_type):
        return [item_type]

class Skill(GameProtocol):
    def __init__(self):
        pass
    
    def pack(self):
        return []
    
    @classmethod
    def unpack(cls, a=None):
        return []