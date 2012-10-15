#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import HOSTNAME, IN_PORT, OUT_PORT, TILESIZE

from share.protocol_lib import Packer, send, receivable
from share.game_protocol import *
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
      
        fileno = sock.fileno()
        
        return sock, fileno
    
    def handle_write(self):
        "отправляет ответы серверу из очереди"
        if self.out_messages:
            for message in self.out_messages:
                send(self.outsock, message)
            self.out_messages = []
    
    def pop_messages(self):
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
                    if self.accept_message:
                        self.read(message)
                    else:
                        self.accept_(message)
                else:
                    break
                

    def socket_loop(self):
        #input events
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
class GameClient(SocketClient, Packer):
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
        if action=='NewWorld':
            self.accept_message = message
        else:
            raise Error('not accepted')
        
    def send_move(self, vector):
        message = self.pack(Move(vector))
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
        message = self.pack(Strike(vector))
        self.put_message(message)
    
    def send_skill(self):
        message = self.pack(Skill())
        self.put_message(message)
        
    def read(self, package):
        if package:
            unpacked = self.unpack(package)
            if unpacked:
                action, message = unpacked
                self.in_messages.append((action, message))
              
    
def main():
	c = Client()
	return 0

if __name__ == '__main__':
	main()
