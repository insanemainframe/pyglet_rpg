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

