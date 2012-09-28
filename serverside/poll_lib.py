#!/usr/bin/env python
# -*- coding: utf-8 -*-
#POLLING LAYER
#классы для работы с событиями сокетов и таймеров
from sys import path; path.append('../')

from config import *
#####################################################################
#EVENT poller
class EventServer:
    poll_engine = 'event(libevent)'
    def __init__(self):
        pass
    def register_accept(self,fileno, stream):
        event.read(fileno, self.handle_accept, stream)
    
    def register(self, address, in_fileno, out_fileno):
        return True
    
    def register_read(self, fileno, address):
        event.read(fileno, self.handle_read, address)
    
    def unregister(self, address, in_fileno, out_fileno):
        return False
    
    def stop_poll(self):
        event.abort()
        
    def run_poll(self):
        event.timeout(self.timer_value, self.timer_handler)
        event.dispatch()
#####################################################################

####EPOLLL poller
class EpollServer:
    poll_engine = 'linux epoll'
    def __init__(self):
        self.poll = epoll()
        self.clients= {}
        
    def register_accept(self, fileno, stream):
        self.poll.register(fileno, EPOLLIN)
        
    def register(self, address, in_fileno, out_fileno):
        self.clients[address] = fileno_tuple(in_fileno, out_fileno)
        return True
        
    def register_read(self, fileno, address):
        self.poll.register(fileno, EPOLLIN)
        
    def unregister(self, address, in_fileno, out_fileno):
        self.poll.unregister(in_fileno)
        self.poll.unregister(out_fileno)
        del  self.clients[address]
        
    def stop_poll(self):
        self.running = False
        self.poll.unregister(self.in_fileno)
        self.poll.unregister(self.out_fileno)
    def get_address(self, fileno):
        for address, pair in self.clients.items():
            if fileno in pair:
                return address
        
    def timer_thread(self):
        while self.running:
            sleep(self.timer_value)
            try:
                self.timer_handler()
            except Exception, exception:
                print 'EXCEPTION IN THREAD', type(exception)
                print exception
                raise exception
    def run_poll(self):
        self.running = True
        thread = threading.Thread(target=self.timer_thread)
        thread.daemon=True
        thread.start()
        while 1:
            events = self.poll.poll()
            for fileno, event in events:
                try:
                    if fileno==self.in_fileno:
                        self.handle_accept(IN)
                    elif fileno==self.out_fileno:
                        self.handle_accept(OUT)
                    elif event==EPOLLIN: 
                        address = self.get_address(fileno)
                        self.handle_read(address)
                except socket.error as Error:
                    self.handle_error(Error, fileno, event)
        
#####################################################################        
#выбираем подходящий полер
try:
    import event
except ImportError:
    try:
        from select import epoll, EPOLLIN, EPOLLOUT
        import threading
        from time import sleep
        import socket
        IN, OUT = 0,1
        from collections import namedtuple
        fileno_tuple = namedtuple('fileno_tuple',('in_','out_'))
    except ImportError:
        try:
            from gevent import core
        except ImportError:
            print 'No polling module(epoll, event, gevent)'
        else:
            PollServer = GeventServer
    else:
        PollServer = EpollServer
else:
    PollServer = EventServer
