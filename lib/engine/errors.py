#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from server_logger import debug


class AlreadyBlocked(BaseException):
	pass


class NoPlaceException(Exception):
    pass


class UnknownAction(Exception):
    pass


class ActionDenied(Exception):
    pass


class ActionError(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return 'ActionError: %s' % self.message