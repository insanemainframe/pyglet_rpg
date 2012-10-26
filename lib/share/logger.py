#!/usr/bin/env python
# -*- coding: utf-8 -*-
#logging
import os.path
import logging

def create_logger(name):
    logfile = '/tmp/%s_rpg.log' % name
    if os.path.exists(logfile):
        from os import remove
        remove(logfile)

    logger = logging.getLogger('%s_rpg' % name)
    hdlr = logging.FileHandler(logfile)

    formatter = logging.Formatter('%(message)s')
    hdlr.setFormatter(formatter)

    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)
    return logger

SERVERLOG = create_logger('server')
CLIENTLOG = create_logger('client')
PROTOCOLLOG = create_logger('protocol')
ENGINELOG = create_logger('engine')
