#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
HOSTNAME = '127.0.0.1'
IN_PORT = 1488
OUT_PORT = 1489
#
TILESIZE = 40
PLAYERSPEED = 80
BALLSPEED = 10
BALLLIFETIME = 30
BLOCKTILES = ['stone', 'water', 'forest']
ANIMATED_TILES = [] #['player']
#
ROUND_TIMER = 0.1
SERVER_TIMER = 0.1

PROFILE = 0
EOL = '\n'


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
