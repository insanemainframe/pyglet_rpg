#!/usr/bin/env python
# -*- coding: utf-8 -*-
#logging
import os.path
import logging


logfile = '/tmp/pyglet_rpg.log'
if os.path.exists(logfile):
    from os import remove
    remove(logfile)

if __debug__ or True:
    handler = logging.StreamHandler()
    

logger = logging.Logger('logger')

formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def print_log(*args):
	message = ' '.join([str(a) for a in args])
	logger.debug(message)

