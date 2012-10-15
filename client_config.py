#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    import pyglet
except ImportError:
    try:
        import pygame
    except ImportError:
        raise ImportError('GameEngine(pyagme or pyglet) not found')
    else:
        CLIENTENGINE = 'pygame'
else:
    CLIENTENGINE = 'pyglet'


TILESDIR = 'images/'
PROFILE_CLIENT = 0
CLIENT_PROFILE_FILE = '/tmp/game_client.stat'
