#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
from socket import htonl, ntohl, error as socket_error
from marshal import loads as marshal_loads, dumps as marshal_dumps

from zlib import compress, decompress

from share.logger import PROTOCOLLOG as LOG

#####################################################################
#исключения для ошибок работы протокола

class PackageError(Exception):
    "ошибка полуения пакета"
    def __init__(self, data=''):
        self.error = 'package receive erroor %s' %  data
    def __str__(self):
        return self.error

class MethodError(Exception):
    "неизвестное действие"
    def __init__(self, action, data=''):
        self.error = 'unknown method %s data \n %s' % (action, data)
    def __str__(self):
        return self.error

class MarshalError:
    "шибка распаковки/упаковки marshal"
    def __init__(self, error, data):
        self.error = error
        self.data = data
    def __str__(self):
        return ' MarshalError %s \n%s' % (self.error, self.data)

class ZlibError:
    "ошибка сжатия или распаковки zlib"
    def __init__(self, error, data):
        self.error = error
        self.data = data
    def __str__(self):
        return ' ZlibError %s \n%s' % (self.error, self.data)

#####################################################################
#упаковка и распаковка пакетов для сокетов
def send(channel, data):
    try:
        value = htonl(len(data))
        size = struct.pack("L",value)
        channel.send(size)
        channel.send(data)
    except socket_error as Error:
        LOG.error('protocol_lib.send error %s' % Error)
    

def receive(channel):
    "получает пакет данных из сокета"
    size = channel.recv(struct.calcsize("L"))
    try:
        size = ntohl(struct.unpack("L", size)[0])
    except struct.error, e:
        LOG.error('protocol_lib.receive struct error %s size %s' % (e,size))
        return ''
    
    data = ""
    while len(data) < size:
        try:
            data+=channel.recv(size - len(data))
            
        except socket_error as Error:
            errno = Error[0]
            if errno!=11:
                LOG.error('protocol_lib.receive error %s' % Error)
                self.handle_error(Error, address)
                return ''
    return data

def receivable(channel):
    "корути получающий данные из сокета"
    while 1:
        #получаем размер из канала
        while 1:
            try:
                size = channel.recv(struct.calcsize("L"))
            except socket_error as Error:
                if Error[0]==11:
                    yield None
                else:
                    raise Error
            else:
                break
        
        print 'recv SIZE'
        #преобразуем размер
        try:
            size = ntohl(struct.unpack("L", size)[0])
        except struct.error, e:
            LOG.error('protocol_lib.receive struct error %s size %s' % (e,size))
            raise PackageError
        
        else:
            #получаем пакет данных
            first = True
            data = ''
            while len(data)<size:
                #print 'RECEVING PACKAGE ', len(data), size
                try:
                    data+=channel.recv(size - len(data))
                except socket_error as Error:
                    if Error[0]==11:
                        print 'err11'
                        yield None
                    else:
                        raise Error
                else:
                    if not first:
                        yield None
                    else:
                        first = False
            #print 'rECEIVED', size
            yield data
            data = None
            
#####################################################################
#врапперы для маршалинга что бы детектировать ошибки

def loads(data):
    try:
        data = decompress(data)
    except Exception as excp:
        raise ZlibError(excp.message)
    else:
        try:
            return marshal_loads(data)
        except Exception as excp:
            raise MarshalError(excp.message, data)

def dumps(data):
    try:
        data = marshal_dumps(data)
    except Exception as excp:
        print data
        raise MarshalError(excp.message)
    else:
        try:
            return compress(data)
        except Exception as excp:
            raise ZlibError(excp.message, data)

            raise error


#####################################################################


class Packer:
    "упаковщик/распаковщик данных с помощью классов из game_protocol"
    def __init__(self):
        "загружаем классы протоколов"
        import game_protocol
        from types import ClassType
        self.method_handlers = {}
        for name in dir(game_protocol):
            Class = getattr(game_protocol, name)
            if type(Class) is ClassType:
                if issubclass(Class, game_protocol.GameProtocol):
                    self.method_handlers[name] = Class()

    def pack(self,data, method):
        "упаковщик данных"
        if method in self.method_handlers:
            try:
                data = self.method_handlers[method].pack(data)
            except Exception as error:
                print 'pack error in method %s with %s' % (method, data)
                raise error
            else:
                try:
                    result = dumps((method, data))
                    return result
                except Exception as excp:
                    raise MarshalError(excp, data)
                    raise excp
        else:
            print 'MethodError'
            raise MethodError(method, data)
    
    def unpack(self, data):
        "распаковщик"
        try:
            data = loads(data)
        except Exception as Error:
            raise MarshalError(Error, data)
        else:
            method, data = data
            if method in self.method_handlers:
                try:
                    message = self.method_handlers[method].unpack(data)
                except Exception, excp:
                    print 'Unpack errror:%s %s %s' % (method, excp, str(data))
                    raise excp
                else:
                    return method, message
            else:
                raise MethodError(method,data)


