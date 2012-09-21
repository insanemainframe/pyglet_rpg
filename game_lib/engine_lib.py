#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import path
path.append('../')


from game_lib import game


from config import *

class UnknownAction(Exception):
    pass


class ActionDenied(Exception):
    pass

#####################################################################
class GameObject:
    alive = True
    def __init__(self, name):
        self.name = name
    
    def handle_action(self, action, args):
        if hasattr(self, action):
            return getattr(self, action)(*args)
        else:
            raise ActionError('no action %s' % action)
    
    def update(self):
        pass
    
    def add_update(self, *args):
        game.add_update(self.name)
    def handle_response(self):
        return []

#####################################################################

class Guided(GameObject):
    "управляемый игроком объекта"
    pass
    


    

#####################################################################
if __name__=='__main__':
    m = Movable(Point(3000,3000), PLAYERSPEED)
















            
