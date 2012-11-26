#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import IN_PORT, OUT_PORT, SOCKET_SERVER_PROFILE, SOCKET_SERVER_PROFILE_FILE
from server_logger import debug

import socket
from socket import error as socket_error

from threading import Thread
from multiprocessing import Process, Event, Pipe

from sys import exc_info, exit as sys_exit
import traceback
import cProfile

from collections import namedtuple
import signal


from serverside.errors import *

from share.protocol_lib import send, Receiver, PackageError
from serverside.multiplexer import Multiplexer
from share.serialization import loads, dumps
from share.packer import pack, unpack


IN, OUT = 0, 1
PORTS = {IN: IN_PORT, OUT: OUT_PORT}


class HandleAcceptError(BaseException):
    pass


client_tuple = namedtuple('client_tuple', ('insock', 'outsock', 'generator'))


class SocketServer(Multiplexer, Process):
    "получает/отправляет данные через сокеты"
    def __init__(self, hostname, listen_num=100):
        Process.__init__(self)
        Multiplexer.__init__(self)

        self.daemon = True

        self.listen_num = listen_num
        self.hostname = hostname

        self.insock, self.in_fileno = self._create_socket(IN)
        self.outsock, self.out_fileno = self._create_socket(OUT)

        self.infilenos = {}
        self.outfilenos = {}

        self.address_buf = {}

        self._accepted, self.__accepted = Pipe(False)
        self._closed, self.__closed = Pipe(False)
        # self._exceptions, self.__exceptions = Pipe(False)
        self._exceptions = Event()

        self._requestes, self.__requestes = Pipe(False)
        self.__responses, self._responses  = Pipe(False)

        self.__sender_thread  = Thread(target = self._sender)
        self.__sender_thread.daemon = True

        self.clients = {}
        self.client_counter = 0

        self.stop_event = Event()
                
        self.r_times = []
        self.running = False


    #интерфейс
    def get_accepted(self, blocking = False):
        while self._accepted.poll():
            yield self._accepted.recv()

    def get_closed(self):
        while self._closed.poll():
            yield self._closed.recv()

    def get_requestes(self):
        while self._requestes.poll():
            client, request = self._requestes.recv()
            yield client, unpack(request)

    def has_exceptions(self):
        return self._exceptions.is_set()

    def put_response(self, client_name, response):
        if not self.stop_event.is_set():
            self._responses.send((client_name, pack(response)))
        else:
            raise ServerStopped

    def run(self):
        signal.signal(signal.SIGINT, lambda *x: self._stop('socket SIGINT %s' % x))
        try:
            if SOCKET_SERVER_PROFILE:
                print 'profile socket-server'
                cProfile.runctx('self._run()', globals(),locals(), SOCKET_SERVER_PROFILE_FILE)
            else:
                self._run()
        except Exception as error:
            debug ('Socket server erro:', error)
            self._handle_exception(*exc_info())
            self._stop('run %s' % str(error))

        debug ('server process stopped')

    def stop(self, sender = 'unknown'):
        debug ('sending signal from %s' % sender)
        self.stop_event.set()

        self._responses.close()
        self._requestes.close()
        self._accepted.close()
        self._closed.close()


    def _handle_exception(self, except_type, except_class, tb):
        debug ('sending exception')
        #self.__exceptions.send((except_type, except_class, traceback.extract_tb(tb)))
        self._exceptions.set()
            
    def _create_socket(self, stream):
        "создает неблокирубщий сокет на заданном порте"
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.hostname, PORTS[stream]))
        sock.setblocking(0)
        fileno = sock.fileno()
        return sock, fileno

    def _sender(self):
        try:
            while not self.stop_event.is_set():
                if self.__responses.poll(3):
                    client_name, response = self.__responses.recv()

                    if client_name in self.clients:
                        sock = self.clients[client_name].outsock

                        package = dumps(response)
                        try:
                            send(sock, package)
                        except socket_error as error:
                            debug('sender error', str(error))
        # except Exception as error:
        #     debug ('excption in sender %s' % str(error))
        #     self._handle_exception(*exc_info())
        #     #self._stop('sender')
        finally:
            self.stop_event.set()

        debug('sender stop')          

    
    def _handle_read(self, client_name):
        "читает один пакет данных из сокета, если это возможно"
        try:
            package = self.clients[client_name].generator.next()

        except socket.error as (errno, message):
            self._handle_close(client_name, 'Socket Error %s %s' % errno, message)
            return False
                            
        except PackageError:
            #если возникла ошабка в пакете - закрываем"
            self._handle_close(client_name, 'PackageError')
            return False
            
        except StopIteration:
            #если клиент отключился"
            self._handle_close(client_name, 'Disconnect')
            return False
        else:
            if package:
                request = loads(package)
                self.__requestes.send((client_name, request))
            return True
            
        
    def _handle_accept(self, stream):
        "прием одного из двух соединений"
        if stream==IN:
            conn, (address, fileno) = self.insock.accept()
            conn.setblocking(0)
            debug('input Connection from %s (%s)' % (fileno, address))
            
        elif stream==OUT:
            conn, (address, fileno) = self.outsock.accept()
            conn.setblocking(0)
            ('output Connection from %s (%s)' % (fileno, address))
        else:
            raise HandleAcceptError('unknnown stream %s' % stream)
        
        conn.setblocking(0)
        
        if address not in self.address_buf:
            self.address_buf[address] = conn
        else:
            if stream==IN:
                insock = conn
                outsock = self.address_buf[address]

            else:
                 outsock = conn
                 insock = self.address_buf[address]
                 
            del self.address_buf[address]
            
            self._accept_client(insock, outsock)
        return True
                 
    def _accept_client(self, insock, outsock):
        "регистрация клиента, после того как он подключился к обоим сокетам"
        client_name = 'player_%s' % self.client_counter
        self.client_counter+=1
        
        self.clients[client_name] = client_tuple(insock,outsock, Receiver(insock))
        
        insock_fileno = insock.fileno()
        outsock_fileno = outsock.fileno()
        
        self.infilenos[insock_fileno] = client_name
        self.outfilenos[outsock_fileno] = client_name
        
        self._register_in(insock_fileno)
        
        debug('accepting_client %s' % client_name)

        #реагируем на появление нового клиента
        self.__accepted.send(client_name)


    def _run(self):
        self.running = True

        self.insock.listen(self.listen_num)
        self.outsock.listen(self.listen_num)
        
        #регистрируем сокеты на ожидание подключений
        self._register_in(self.insock.fileno())
        self._register_in(self.outsock.fileno())
       
        debug('\nServer running at %s:(%s,%s) multiplexer: %s \n' % (self.hostname, IN_PORT, OUT_PORT, self.poll_engine))
        #запускаем sender
        self.__sender_thread.start()
    
        #запускаем мультиплексор
        self._run_poll()
    
    
    def _handle_close(self, client_name, message):
        "закрытие подключения"
        debug('Closing %s: %s' % (client_name, message))
        
        self.__closed.send(client_name)
        
        infileno = self.clients[client_name].insock.fileno()
        outfileno = self.clients[client_name].outsock.fileno()
        
        self._unregister(infileno)
        
        del self.infilenos[infileno]
        del self.outfilenos[outfileno]
        
        #закрываем подключения и удаляем
        
        self.clients[client_name].insock.close()
        self.clients[client_name].outsock.close()
        del self.clients[client_name]


    def _sigint(self, sig_num, frame):
        self.stop_event.set()

    def _stop(self, reason=None):
        debug('SocketServer stopping.. %s' % str(reason))

        self.running = False

        if not self.stop_event.is_set():
            self.stop_event.set()

        self.__responses.close()
        self.__requestes.close()
        self.__accepted.close()
        self.__closed.close()

        self._unregister(self.in_fileno)
        self.insock.close()
        self.outsock.close()
        self._stop_poll()
        
        debug( 'waiting for sender thread')
        self.__sender_thread.join()
        debug('SocketServer stopped')

 
            
        
    
    

        


