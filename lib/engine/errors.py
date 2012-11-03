#!/usr/bin/env python
# -*- coding: utf-8 -*-
class NoPlaceException(BaseException):
    pass

class UnknownAction(BaseException):
    pass


class ActionDenied(BaseException):
    pass

class ActionError(BaseException):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return 'ActionError: %s' % self.message