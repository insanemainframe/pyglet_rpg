#!/usr/bin/env python
# -*- coding: utf-8 -*-
#logging
import os.path
import logging

from config import LOG_FILE

if os.path.exists(LOG_FILE):
    from os import remove
    remove(LOG_FILE)

if __debug__:
    handler = logging.StreamHandler()

else:
	handler = logging.FileHandler(LOG_FILE)
    

logger = logging.Logger('logger')

formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def debug(*args):
	message = ' '.join([str(a) for a in args])
	logger.debug(message)

