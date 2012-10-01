#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from client_config import CLIENTENGINE

if CLIENTENGINE=='pyglet':
    from pyglet_window import GameWindow, GUIWindow, Label, ClockDisplay, create_tile, create_label
else:
    from pygame_window import GameWindow, GUIWindow, Label, ClockDisplay, create_tile, create_label
