#!/usr/bin/env python
# -*- coding: utf-8 -*-
import struct
from socket import htonl, ntohl, error as socket_error
from marshal import loads as marshal_loads, dumps as marshal_dumps
#from json import loads as marshal_loads, dumps as marshal_dumps

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
        size = struct.pack("!Q",value)
        channel.send(size)
        channel.send(data)
    except socket_error as Error:
        LOG.error('protocol_lib.send error %s' % Error)
    


def receivable(channel):
    "генератор получающий данные из сокета, возвращает пакет данных или None если считывать больше нечего"
    while 1:
        #получаем размер из канала
        size_for_recv= struct.calcsize("!Q")
        size = ''
        while len(size)<size_for_recv:
            try:
                new_size = channel.recv(size_for_recv-len(size))
                
            except socket_error as Error:
                errno = Error[0]
                if errno==11:
                    #сокет недоступен для чтения
                    yield None
                elif errno==35:
                    print 'socket error 35'
                    yield None
                else:
                    print 'receivable socket error#', str(errno)
                    raise Error
            else:
                if new_size:
                    size+=new_size
                else:
                    print 'NO SIZE'
                    raise StopIteration
        if not size:
            raise StopIteration
        
        #преобразуем размер
        try:
            size = ntohl(struct.unpack("!Q", size)[0])
        except struct.error, e:
            #в случае ошибки конвертации размера
            print 'protocol_lib.receive struct error %s size %s' % (e, len(size))
            #raise PackageError
            yield None
        else:
            #получаем пакет данных
            data = ''
            while len(data)<size:
                try:
                    new_data = channel.recv(size - len(data))
                except socket_error as Error:
                    errno = Error[0]
                    if errno==11:
                        #сокет недоступен для чтения
                        yield None
                    elif errno==35:
                        print 'socket error 35'
                        yield None
                    else:
                        print 'socket error while receiving apckage: %s' % str(Error)
                        raise Error
                else:
                    if new_data:
                        data+=new_data
                    else:
                        print 'NO DATA'
                        raise StopIteration

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
        raise MarshalError(excp.message, data)
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
                data = self.method_handlers[method].pack(*data)
            except Exception as error:
                print 'pack error in method %s with %s' % (method, data)
                raise error
            else:
                try:
                    result = dumps((method, data))
                    return result
                except MarshalError:
                    print 'MarshalError', method, data
                    return ''
        else:
            print 'MethodError'
            raise MethodError(method, data)
    
    def unpack(self, data):
        "распаковщик"
        try:
            data = loads(data)
        except MarshalError:
            print 'MarshalError'
            return None
        else:
            method, data = data
            if method in self.method_handlers:
                try:
                    message = self.method_handlers[method].unpack(*data)
                except Exception, excp:
                    print 'Unpack errror:%s %s %s' % (method, excp, str(data))
                    raise excp
                else:
                    return method, message
            else:
                raise MethodError(method,data)


