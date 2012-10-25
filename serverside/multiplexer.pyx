#!/usr/bin/env python
# -*- coding: utf-8 -*-
from socket import error as socket_error

from config import *

IN, OUT = 0,1


class EpollMultiplexer:
    poll_engine = 'linux epoll'
    def __init__(self):
        self._poller = epoll()
    
    def _register_in(self, int fileno):
        self._poller.register(fileno, EPOLLIN)
        
    
    def _unregister(self, int fileno):
        self._poller.unregister(fileno)
    
    def _run_poll(self):
        cdef int fileno, event
        cdef list event_pairs

        print('Start polling')
        while not self.stop_event.is_set():
            event_pairs = self._poller.poll()
            while event_pairs:
                fileno, event = event_pairs.pop()
                try:
                    if fileno==self.in_fileno:
                        self._handle_accept(IN)
                        
                    elif fileno==self.out_fileno:
                        self._handle_accept(OUT)
                        
                    elif event==EPOLLIN: 
                        if fileno in self.infilenos:
                            client_name = self.infilenos[fileno]
                            self._handle_read(client_name)
                    
                    elif event==EPOLLHUP:
                        self._handle_error(Error, fileno, event)
                            
                except socket_error as Error:
                    print 'socket_error', Error
                    self._handle_error(Error, fileno, event)
        print 'polling end'


class SelectMultiplexer:
    poll_engine = 'select'
    def __init__(self):
        pass
    
    def _register(self, fileno):
        pass
        
    def _unregister(self, fileno):
        pass

    def _register_in(self, fileno):
        pass
        
    def _run_poll(self):
        "ожидание входящих пакетов с совкетов, обработка новых подключений"
        print('Start polling')
        while not self.stop_event.is_set():
            print('polling')
            #смотрим новые подключения и на чтение
            insocks = [client.insock for client in self.clients.values()]
            timeout = SERVER_TIMER*1.5  #- (time()-t)
            events = select([self.insock,self.outsock]+insocks,[],[],timeout)[0]
            for sock in events:
                fileno = sock.fileno()
                if fileno==self.in_fileno:
                    self._handle_accept(IN)
                elif fileno==self.out_fileno:
                    self._handle_accept(OUT)
                else:
                    client_name = self.infilenos[fileno]
                    self._handle_read(client_name)
            self.write_all()

        print('Stop polling')





try:
    from select import epoll, EPOLLIN, EPOLLOUT, EPOLLHUP

except ImportError:
    from select import select
    Multiplexer = SelectMultiplexer

else:
    Multiplexer = EpollMultiplexer

