#!/usr/bin/env python
# -*- coding: utf-8 -*-
from re import match
from sys import argv

PATTERN = '^\d+\.\d+\.\d+\.\d+$'

def ask_hostname(default):
    
    if len(argv)>1:
        if argv[1]=='-d':
            return default
    message = 'Enter hostname or press Enter for default %s: ' % default
    while 1:
        result = raw_input(message)
        if not result:
            return default

        if match(PATTERN, result):
            return result
        else:
            print('wrong format')