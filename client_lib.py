#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket, sys, os, select
from protocol import *

from config import HOSTNAME, IN_PORT, OUT_PORT
EOL = '\n'

class EpollClient:
    def __init__(self):
        self.epoll = select.epoll()
        self.buff = ''
        
        self.insock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.insock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.insock.connect((HOSTNAME,IN_PORT))
        self.insock.setblocking(0)
        self.in_fileno = self.insock.fileno()
        self.epoll.register(self.in_fileno, select.EPOLLIN)
        
        self.outsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.outsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.outsock.connect((HOSTNAME,OUT_PORT))
        self.outsock.setblocking(0)
        self.out_fileno = self.outsock.fileno()
        self.epoll.register(self.out_fileno, select.EPOLLOUT)
        		
        
        self.events = self.epoll.poll()
    
    def handle_write(self):
        print 'handle_Write'
        for message in self.out_messages:
            self.socket.send(dumps(message)+EOL)
        self.epoll.modify(self.fileno, select.EPOLLIN)
    
    def put_message(self, message):
        print 'put_message', message
        self.out_messages.append(message)
        self.epoll.modify(self.fileno, select.EPOLLOUT)
    
    def handle_read(self):
        print 'handle_read'
        try:
            data = self.socket.recv(1024)
        except socket.error, err:
            print 'socket.error', err
            if err[0]!=11:
                raise err
            else:
                return []
        else:
            messages = []
            for char in data:
                if char!=EOL:
                    self.buff+=char
                else:
                    messages.append(self.buff)
                    self.buff=''
            for message in messages:
                if not self.accept_message:
                    self.accept(message)
                else:
                    self.receive(message)
        finally:
            print 'modify to OUT'
            self.epoll.modify(self.fileno, select.EPOLLOUT)
    
    def loop(self):
        for fileno, event in self.events:
            try:
                if event & select.EPOLLIN: 
                    self.handle_read()
                elif event & select.EPOLLOUT:
                    self.handle_write()
                elif event & select.EPOLLHUP: 
                    self.handle_close()
            except socket.error as Error:
                self.handle_error(Error)
    
    def handle_close(self):
        print 'connection closed'
    def handle_error(Error):
        print Error
        sys.exit()
    
            
class Client(EpollClient):
    def __init__(self):
        EpollClient.__init__(self)
        self.accept_message = False
        self.in_messages = []
        self.out_messages = []
        
    def accept(self, message):
        self.accept_message = unpack_server_accept(message)
        
    def send(self, vector):
        self.put_message(dumps(vector.get()))
        
    
    def receive(self, message):
        print 'client.receive', message
        move_vector, land, objects, objects_updates = unpack_server_message(message)
        self.in_messages.append((move_vector, land, objects, objects_updates))
              
    

    
def main():
	c = Client()
	return 0

if __name__ == '__main__':
	main()

