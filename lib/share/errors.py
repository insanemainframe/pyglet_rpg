#!/usr/bin/env python
# -*- coding: utf-8 -*-
class PackageError(BaseException):
    "ошибка полуения пакета"

class MarshalError(Exception):
    "шибка распаковки/упаковки marshal"
    def __init__(self, error, data):
        Exception.__init__(self)
        self.error = error
        self.data = data
    def __str__(self):
        return ' MarshalError %s \n%s' % (self.error, self.data)


class ZlibError(Exception):
    "ошибка сжатия или распаковки zlib"
    def __init__(self, error, data):
        Exception.__init__(self)
        self.error = error
        self.data = data
    def __str__(self):
        return ' ZlibError %s \n%s' % (self.error, self.data)


class MethodError(Exception):
    "неизвестное действие"
    def __init__(self, action, data=''):
        Exception.__init__(self)
        self.error = 'unknown method %s data \n %s' % (action, data)
    def __str__(self):
        return self.error