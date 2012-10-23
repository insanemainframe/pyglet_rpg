#!/usr/bin/env python
# -*- coding: utf-8 -*-

def alive_only(Class=None):
    def wrapper(method):
        def wrap(self,*args):
            if self.alive:
                return method(self, *args)
            else:
                if Class:
                    return getattr(Class, method.__name__)(self, *args)
        return wrap
    return wrapper

def player_filter(Class):
    def wrapper(method):
        def wrap(self, player):
            if isinstance(player, Class):
                return method(self,player)
        return wrap
    return wrapper

def player_filter_alive(method):
    def wrap(self, player):
        if player.alive:
            return method(self,player)
    return wrap