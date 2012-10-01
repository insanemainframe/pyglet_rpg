#!/usr/bin/env python
# -*- coding: utf-8 -*-
from select import select, epoll, EPOLLIN, EPOLLOUT
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
                    self.handle_accept(IN)
                elif fileno==self.out_fileno:
                    self.handle_accept(OUT)
                else:
                    client_name = self.infilenos[fileno]
                    self.handle_read(client_name)

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
                    elif event==EPOLLOUT:
                        client_name = self.outfilenos[fileno]
                        self.handle_write(client_name)
                except socket_error as Error:
                    self.handle_error(Error, fileno, event)

class EventMultiplexer:
    poll_engine = 'libevent'
    def __init__(self):
        self.events = {}
    
    def register_in(self, fileno):
        if fileno==self.in_fileno:
            self.events[fileno] = event.read(fileno, self.handle_accept, IN)
        elif fileno==self.out_fileno:
            self.events[fileno] = event.read(fileno, self.handle_accept, OUT)
        else:
            client_name = self.infilenos[fileno]
            self.events[fileno] = event.read(fileno, self.handle_read, client_name)
    
    def register_out(self, fileno):
        client_name = self.outfilenos[fileno]
        self.events[fileno] = event.write(fileno, self.handle_write, client_name)
    
    def unregister(self, fileno):
        self.events[fileno].delete()
    
    def run_poll(self):
        event.dispatch()

class GeventMultiplexer:
    poll_engine = 'gevent'
    def __init__(self):
        self.events = {}
    
    def cb_accept(self, event, evtype):
        return self.handle_accept(event.arg)
        
    def cb_read(self, event, evtype):
        print 'cb_read', event.arg
        client_name = event.arg
        return self.handle_read(client_name)
        
    def cb_write(self, event, evtype,):
        print 'cb_write', event.arg
        client_name = event.arg
        return self.handle_write(client_name)
    
    def register_in(self, fileno):
        if fileno==self.in_fileno:
            event = core.event(core.EV_READ, fileno, self.cb_accept, IN)
        elif fileno==self.out_fileno:
            event = core.event(core.EV_READ, fileno, self.cb_accept, OUT)
        else:
            client_name = self.infilenos[fileno]
            event = core.event(core.EV_READ, fileno, self.cb_read, client_name)
        self.events[fileno] = event
        event.add()
    
    def register_out(self, fileno):
        client_name = self.outfilenos[fileno]
        event = core.event(core.EV_WRITE, fileno, self.cb_write, client_name)
        self.events[fileno] = event
        event.add()
    
    def unregister(self, fileno):
        self.events[fileno].delete()
    
    def run_poll(self):
        core.dispatch()


try:
    import event
except ImportError:
    try:
        from gevent import core
    except ImportError:
        try:
            from select import epoll, EPOLLIN, EPOLLOUT
        except ImportError:
            from select import select
            Multiplexer = SelectMultiplexer
        else:
            Multiplexer = EpollMultiplexer
    else:
        
        Multiplexer = GeventMultiplexer
else:
    Multiplexer = EventMultiplexer

