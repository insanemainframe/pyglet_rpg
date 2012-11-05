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


class MarshalError(BaseException):
    "шибка распаковки/упаковки marshal"
    def __init__(self, error, data):
        BaseException.__init__(self)
        self.error = error
        self.data = data
    def __str__(self):
        return ' MarshalError %s \n%s' % (self.error, self.data)

class ZlibError(BaseException):
    "ошибка сжатия или распаковки zlib"
    def __init__(self, error, data):
        BaseException.__init__(self)
        self.error = error
        self.data = data
    def __str__(self):
        return ' ZlibError %s \n%s' % (self.error, self.data)


class MethodError(BaseException):
    "неизвестное действие"
    def __init__(self, action, data=''):
        BaseException.__init__(self)
        self.error = 'unknown method %s data \n %s' % (action, data)
    def __str__(self):
        return self.error