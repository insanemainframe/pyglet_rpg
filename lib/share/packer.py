#!/usr/bin/env python
# -*- coding: utf-8 -*-
from share.errors import MethodError

from share import game_protocol
from share.gameprotocol.meta import GameProtocol


method_handlers = {}

for name in dir(game_protocol):
    Class = getattr(game_protocol, name)
    if type(Class) is type:
        if issubclass(Class, game_protocol.GameProtocol):
            method_handlers[name] = Class


def pack(protocol_object):
    "упаковщик данных"
    assert isinstance(protocol_object, game_protocol.GameProtocol)

    data = protocol_object.pack()
    method = protocol_object.__class__.__name__
    
    return (method, data)
    
    
def unpack(pair):
    "распаковщик"
    method, data= pair
    if method in method_handlers:
        message = method_handlers[method].unpack(*data)
        return str(method), message
    else:
        raise MethodError(method,data)





