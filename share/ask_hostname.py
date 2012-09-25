#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from sys import argv

class AskHostname:
    def __init__(self, hostname):
        self.default = hostname
        self.pattern = '^\d+\.\d+\.\d+\.\d+$'
        if len(argv)>1:
            if argv[1]=='-d':
                self.hostname = self.default
                return
        message = 'Enter hostname or press Enter for default %s: ' % self.default
        while 1:
            result = raw_input(message)
            if not result:
                self.hostname = self.default
                break
            elif self.check(result):
                self.hostname = result
                break
            else:
                print 'invalid value: %s' % self.error
    
    def check(self, message):
        if re.match(self.pattern, message):
            return True
        else:
            self.error = 'wrong format'        
            return False
