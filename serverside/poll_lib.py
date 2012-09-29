#!/usr/bin/env python
# -*- coding: utf-8 -*-
from select import select, epoll, EPOLLIN, EPOLLOUT

from config import *

IN, OUT = 0,1


class SelectServer:
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
                    self.handle_accept(IN)
                elif fileno==self.out_fileno:
                    self.handle_accept(OUT)
                else:
                    client_name = self.infilenos[fileno]
                    self.handle_read(client_name)

class EpollServer:
    poll_engine = 'linux epoll'
    def __init__(self):
        self.poller = epoll()
    
    def register(self, fileno):
        self.poller.register(fileno, EPOLLIN)
    
    def unregister(self, fileno):
        self.poller.unregister(fileno)
    
    def run_poll(self):
         while 1:
            events = self.poller.poll()
            for fileno, event in events:
                try:
                    if fileno==self.in_fileno:
                        self.handle_accept(IN)
                    elif fileno==self.out_fileno:
                        self.handle_accept(OUT)
                    elif event==EPOLLIN: 
                        client_name = self.infilenos[fileno]
                        self.handle_read(client_name)
                except socket.error as Error:
                    self.handle_error(Error, fileno, event)

class EventServer:
    poll_engine = 'libevent'
    def __init__(self):
        pass
    
    def register(self, fileno):
        if fileno==self.in_fileno:
            event.read(fileno, self.handle_accept, IN)
        elif fileno==self.out_fileno:
            event.read(fileno, self.handle_accept, OUT)
        else:
            client_name = self.infilenos[fileno]
            event.read(fileno, self.handle_read, client_name)
    
    def unregister(self, fileno):
        return False
    
    def run_poll(self):
        event.dispatch()

try:
    import event
except ImportError:
    try:
        from select import epoll, EPOLLIN, EPOLLOUT
    except ImportError:
        from select import select
        PollServer = EpollServer
    else:
        PollServer = EpollServer
else:
    PollServer = EventServer

