#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import HOSTNAME, IN_PORT, OUT_PORT, TILESIZE

from share.protocol_lib import Packer, send, receivable
from share.mathlib import *

import socket, sys, os

from select import select



#####################################################################
IN, OUT = 0,1
PORTS = {IN:IN_PORT, OUT:OUT_PORT}

class SocketClient:
    "класс работы с сокетами и селектом"
    def __init__(self):
        self.buff = ''
        self.outsock, self.out_fileno = self.create_sock(IN)
        
        self.insock, self.in_fileno = self.create_sock(OUT)
        #self.poller.register(self.in_fileno, EPOLLIN)
        
        self.generator = receivable(self.insock)
        
        self.out_messages = []
        
        self.in_messages = []        
        
        
    def create_sock(self, stream):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print 'connect to %s:%s' % (self.hostname, PORTS[stream])
        sock.connect((self.hostname, PORTS[stream]))
        sock.setblocking(0)
        if stream==OUT:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        fileno = sock.fileno()
        
        return sock, fileno
    
    def handle_write(self):
        "отправляет ответы серверу из очереди"
        if self.out_messages:
            for message in self.out_messages:
                send(self.outsock, message)
            self.out_messages = []
            
    def put_message(self, message):
        "кладет ответ в очередь на отправку"
        self.out_messages.append(message)
    
    def handle_read(self):
        "читает все пакеты, пока сокет доступен"
        while 1:
            message = self.generator.next()
            if message:
                if self.accept_message:
                    self.read(message)
                else:
                    self.accept_(message)
            else:
                break
                

    def socket_loop(self):
        #input events
        inevents , outevents, expevents = select([self.insock],[self.outsock],[], 0.1)
        for fileno in inevents:
            try:
                self.handle_read()
            except socket.error as Error:
                self.handle_close()
        #output events
        self.handle_write()
       
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
class Client(SocketClient, Packer):
    "полуение и распаковка сообщений, антилаг"
    antilag= False
    antilag_shift = Point(0,0)   
    accept_message = False
    
    
    def __init__(self):
        SocketClient.__init__(self)
        Packer.__init__(self)

    def wait_for_accept(self):
        print 'waiting for acception'
        while 1:
            self.socket_loop()
            if self.accept_message:
                print 'accepted'
                return self.accept_message

    def accept_(self, message):
        action, message = self.unpack(message)
        if action=='ServerAccept':
            self.accept_message = message
        
    def send_move(self, vector):
        message = self.pack([vector],'Move')
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
        message = self.pack([vector],'Strike')
        self.put_message(message)
    
    def send_skill(self):
        message = self.pack([],'Skill')
        self.put_message(message)
        
    def read(self, package):
        if package:
            action, message = self.unpack(package)
            self.in_messages.append((action, message))
              
    
def main():
	c = Client()
	return 0

if __name__ == '__main__':
	main()
