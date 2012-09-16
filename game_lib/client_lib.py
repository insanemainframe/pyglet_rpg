#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket, sys, os, select

from protocol_lib import pack, unpack, send, receive
from math_lib import Point

from sys import path
path.append('../')
from config import HOSTNAME, IN_PORT, OUT_PORT, TILESIZE

#####################################################################
class SocketClient:
    "класс работы с сокетами и селектом"
    def __init__(self):
        self.hostname = HOSTNAME
        self.buff = ''
        self.outsock, self.out_fileno = self.create_sock(IN_PORT)
        self.insock, self.in_fileno = self.create_sock(OUT_PORT)
        
    def create_sock(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((self.hostname,port))
        sock.setblocking(0)
        fileno = sock.fileno()
        return sock, fileno
    
    def handle_write(self):
        if self.out_messages:
            for message in self.out_messages:
                send(self.outsock, message)
            self.out_messages = []
            
    def put_message(self, message):
        self.out_messages.append(message)
    
    def handle_read(self):
        data = receive(self.insock)
        if data:
            if self.accept_message:
                self.read(data)
            else:
                self.accept_(data)


    def socket_loop(self):
        #input events
        inevents , outevents, expevents = select.select([self.insock],[self.outsock],[])
        for fileno in inevents:
            try:
                self.handle_read()
            except socket.error as Error:
                self.handle_error(Error)
        #output events
        for fileno in outevents:
            try:
                self.handle_write()
            except socket.error as Error:
                self.handle_error(Error)
       
    def close_connection(self):
        self.insock.close()
        self.outsock.close()
        print 'connection closed'
        
    def handle_close(self):
        self.on_close()
        print 'connection closed'
    
    def handle_error(self, Error):
        print 'error', Error
        sys.exit()

#####################################################################
#
class Client(SocketClient):
    "полуение и распаковка сообщений, антилаг"
    antilag= False
    antilag_shift = Point(0,0)   
    accept_message = False
    in_messages = []
    out_messages = []
    
    def __init__(self):
        SocketClient.__init__(self)

    def wait_for_accept(self):
        print 'waiting for acception'
        self.socket_loop()
        if self.accept_message:
            print 'accepted'
            return self.accept_message
        else:
            return False

    def accept_(self, message):
        print 'accept_'
        action, message = unpack(message)
        if action=='server_accept':
            #print 'Client.accept %s' % str(message)
            self.accept_message = message
        
    def send_move(self, vector):
        message = pack(vector,'move_message')
        self.put_message(message)
        #предварительное движение
        if vector and not self.shift and not self.antilag:
                step = vector * ((TILESIZE/5) / abs(vector))
                if step<vector:
                    shift = step
                else:
                    shift = vector
                self.antilag_init(shift)
                self.antilag_shift = shift
                self.antilag = True
        
    def send_ball(self, vector):
        message = pack(vector,'ball_message')
        self.put_message(message)
        
    def read(self, package):
        if package:
            action, message = unpack(package)
            self.in_messages.append((action, message))
              
    
def main():
	c = Client()
	return 0

if __name__ == '__main__':
	main()

