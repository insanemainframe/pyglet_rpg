#!/usr/bin/env python
# -*- coding: utf-8 -*-
from socket import error as socket_error

from config import *

IN, OUT = 0,1


class SelectMultiplexer:
    poll_engine = 'select'
    def __init__(self):
        pass
    
    def register(self, fileno):
        pass
        
    def unregister(self, fileno):
        pass
        
    def run_poll(self):
        "ожидание входящих пакетов с совкетов, обработка новых подключений"
        
        while 1:
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

class EpollMultiplexer:
    poll_engine = 'linux epoll'
    def __init__(self):
        self.poller = epoll()
    
    def register_in(self, fileno):
        self.poller.register(fileno, EPOLLIN)
        
    def register_out(self, fileno):
        self.poller.register(fileno, EPOLLOUT) 
    
    def unregister(self, fileno):
        self.poller.unregister(fileno)
    
    def run_poll(self):
         while 1:
            event_pairs = dict(self.poller.poll())
            while event_pairs:
                fileno, event = event_pairs.popitem()
                try:
                    if fileno==self.in_fileno:
                        self._handle_accept(IN)
                        
                    elif fileno==self.out_fileno:
                        self._handle_accept(OUT)
                        
                    elif event==EPOLLIN: 
                        if fileno in self.infilenos:
                            client_name = self.infilenos[fileno]
                            self._handle_read(client_name)
                            
                    elif event==EPOLLOUT:
                        if fileno in self.outfilenos:
                            client_name = self.outfilenos[fileno]
                            self._handle_write(client_name)
                    
                    elif event==EPOLLHUP:
                        self._handle_error(Error, fileno, event)
                            
                except socket_error as Error:
                    self._handle_error(Error, fileno, event)



try:
    from select import epoll, EPOLLIN, EPOLLOUT, EPOLLHUP

except ImportError:
    from select import select
    Multiplexer = SelectMultiplexer

else:
    Multiplexer = EpollMultiplexer

