#!/usr/bin/env python
# -*- coding: utf-8 -*-
TILESIZE = 40
PLAYERSPEED = 40
BLOCKTILES = ['stone', 'water', 'forest']
ANIMATED_TILES = [] #['player']
ROUND_TIMER = 0.1
SERVER_TIMER = 0.1
HOSTNAME = '127.0.0.1' #'89.105.156.179' #
IN_PORT = 1488
OUT_PORT = 1489
PROFILE = False
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
