#!/usr/bin/env python
# -*- coding: utf-8 -*-
import struct
from socket import htonl, ntohl, error as SocketError





#####################################################################

class PackageError(BaseException):
    "ошибка полуения пакета"
    





#####################################################################
#упаковка и распаковка пакетов для сокетов
def send(channel, data):
    assert isinstance(data, bytes) and bool(data), data

    #вычисляем размер пакета
    size = htonl(len(data))
    size_block = struct.pack("!Q",size)

    response = size_block+data

    response_size = len(response)

    #посылаем размер пакета
    try:
        sended_size = channel.send(response)
    except SocketError as (errno, message):
        if errno in (11, 9, 104, 32):
            print('send: error %s' % errno)
            return

        else:
            raise SocketError(errno, message)
    else:
        assert sended_size == response_size


            

    

size_for_recv= struct.calcsize("!Q")

def Receiver(channel):
    "генератор получающий данные из сокета, возвращает пакет данных или None если считывать больше нечего"
    while 1:
        data = bytes('')
        package_size = bytes('')

        #получаем размер из канала
        while len(package_size)<size_for_recv:
            try:
                new_size = channel.recv(size_for_recv-len(package_size))
                
            except SocketError as (errno, message):
                if errno in (11, 35):
                    yield 
                else:
                    print('Receiver socket error#', errno, message)

                    raise SocketError(errno, message)
            else:
                if new_size:
                    package_size+=new_size
                else:
                    raise StopIteration
        if not package_size:
            raise StopIteration
        
        #преобразуем размер
        try:
            size = struct.unpack("!Q", package_size)[0]
            size = ntohl(size)
        except struct.error as Error:
            #в случае ошибки конвертации размера
            print('protocol_lib.receive struct error %s size %s' % (Error, len(size)))
            raise StopIteration

        else:
            #получаем пакет данных
            while len(data)<size:
                try:
                    new_data = channel.recv(size - len(data))
                
                except SocketError as (errno, message):
                    if errno in (11, 35):
                        yield
                    else:
                        print('Receiver socket error', errno, message)
                        raise  SocketError(errno, message)


                else:
                    if new_data:
                        data+=new_data
                    else:
                        raise StopIteration

            yield data
            
            


