#!/usr/bin/env python
# -*- coding: utf-8 -*-
TILESIZE = 40
PLAYERSPEED = 80
BLOCKTILES = ['stone', 'water', 'forest']
ANIMATED_TILES = [] #['player']
PRESSED_TIMER = 0.5
HOSTNAME = '127.0.0.1'
PORT = 1488
#logging
import os.path
logfile = '/tmp/rpg.log'
if os.path.exists(logfile):
    from os import remove
    remove(logfile)
import logging
logger = logging.getLogger('myapp')
hdlr = logging.FileHandler(logfile)
formatter = logging.Formatter('%(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)
