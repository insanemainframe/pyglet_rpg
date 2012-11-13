#!/usr/bin/env python
# -*- coding: utf-8 -*-
import struct
from socket import htonl, ntohl, error as socket_error

from share.logger import PROTOCOLLOG as LOG




#####################################################################

class PackageError(BaseException):
    "ошибка полуения пакета"
    def __init__(self, data=''):
        self.error = 'package receive erroor %s' %  data
    def __str__(self):
        return self.error





#####################################################################
#упаковка и распаковка пакетов для сокетов
def send(channel, str data):
    if data:
        value = htonl(len(data))
        size = struct.pack("!Q",value)
        #посылаем размер пакета
        while size:
            try:
                channel.send(size)
            except socket_error as Error:
                if Error[0]==11:
                    print('send: error 11')
                if Error[0]==9:
                    pass
                elif Error[0]==104:
                    return 
                elif Error[0]==32:
                    return 
                else:
                    raise Error
            else:
                size = ''
        #посылаем пакет
        while data:
            try:
                channel.send(data)
            except socket_error as Error:
                if Error[0]==11:
                    print('send: error 11')
                elif Error[0]==104:
                    return
                elif Error[0]==32:
                    return 
                else:
                    raise Error
            else:
                data = ''
            

    


def receivable(channel):
    "генератор получающий данные из сокета, возвращает пакет данных или None если считывать больше нечего"
    cdef str data
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
                    yield ''
                elif errno==35:
                    print('socket error 35')
                    yield ''
                else:
                    print('receivable socket error#', str(errno))
                    raise Error
            else:
                if new_size:
                    size+=new_size
                else:
                    raise StopIteration
        if not size:
            raise StopIteration
        
        #преобразуем размер
        try:
            size = struct.unpack("!Q", size)[0]
            size = ntohl(size)
        except struct.error as Error:
            #в случае ошибки конвертации размера
            print('protocol_lib.receive struct error %s size %s' % (Error, len(size)))
            yield ''
        except OverflowError:
            print('OverflowError', size)
            yield ''
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
                        yield ''
                    elif errno==35:
                        print('socket error 35')
                        yield ''
                    else:
                        print('socket error while receiving apckage: %s' % str(Error))
                        raise Error
                else:
                    if new_data:
                        data+=new_data
                    else:
                        print('NO DATA')
                        raise StopIteration

            yield data
            data = None
            


