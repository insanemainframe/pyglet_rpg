#!/usr/bin/env python
# -*- coding: utf-8 -*-
#logging
import os.path
import logging

from config import SERVER_LOG_FILE

if os.path.exists(SERVER_LOG_FILE):
    from os import remove
    remove(SERVER_LOG_FILE)

if __debug__ or True:
    handler = logging.StreamHandler()
    

logger = logging.Logger('logger')

formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def debug(*args):
	message = ' '.join([str(a) for a in args])
	logger.debug(message)

