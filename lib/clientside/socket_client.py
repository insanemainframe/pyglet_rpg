#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import HOSTNAME, IN_PORT, OUT_PORT, ROUND_TIMER


import socket, sys, os
from select import select
from socket import error as SocketError

from share.protocol_lib import send, receivable


IN, OUT = 0,1
PORTS = {IN:IN_PORT, OUT:OUT_PORT}

class SocketClient:
    "класс работы с сокетами и селектом"
    def __init__(self, hostname):
        self.hostname = hostname
        self.buff = ''
        self.outsock, self.out_fileno = self.create_sock(IN)
        
        self.insock, self.in_fileno = self.create_sock(OUT)
        
        self.generator = receivable(self.insock)
        
        self.out_messages = []
        
        self.in_messages = []     
        self.accepted = False   
        
        
    def create_sock(self, stream):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print 'connect to %s:%s' % (self.hostname, PORTS[stream])
        sock.connect((self.hostname, PORTS[stream]))
        sock.setblocking(0)
      
        fileno = sock.fileno()
        
        return sock, fileno
    
    def handle_write(self):
        "отправляет ответы серверу из очереди"
        if self.out_messages:
            for message in self.out_messages:
                send(self.outsock, message)
            self.out_messages = []

    def pop_message(self):
            if self.in_messages:
                return self.in_messages.pop()
            else:
                return False

    def get_messages(self):
        messages = self.in_messages
        self.in_messages = []
        return messages
    
    def put_message(self, message):
        "кладет ответ в очередь на отправку"
        self.out_messages.append(message)
    
    def handle_read(self):
        "читает все пакеты, пока сокет доступен"
        while 1:
            try:
                message = self.generator.next()
            except StopIteration:
                self.handle_close('Disconnect')
            else:
                if message:
                    if self.accepted:
                        self.read(message)
                    else:
                        self.accept_(message)
                else:
                    break

                

    def socket_loop(self):
        inevents , outevents, expevents = select([self.insock],[self.outsock],[], ROUND_TIMER)
        for fileno in inevents:
            try:
                self.handle_read()
            except socket.error as Error:
                if Error[0]==111:
                    self.handle_close('Disconnect')
                else:
                    self.handle_close(str(Error))
        
        for fileno in expevents:
            self.handle_close('select exp')
        #output events
        self.handle_write()
       
    def close_connection(self, message=''):
        self.insock.close()
        self.outsock.close()
        print 'connection closed %s' % message
        
    def handle_close(self, message=''):
        self.on_close()
        print 'Connection closed:%s' % message
    
    def handle_error(self, Error):
        print 'error', Error
        sys.exit()

#####################################################################
#

              
