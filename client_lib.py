#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket, sys, os, select
from protocol_lib import *

from config import EOL, HOSTNAME, IN_PORT, OUT_PORT

class SelectClient:
    def __init__(self):
        self.buff = ''
        
        self.outsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.outsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.outsock.connect((HOSTNAME,IN_PORT))
        self.outsock.setblocking(0)
        self.out_fileno = self.outsock.fileno()
        print 'output connection'
        
        self.insock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.insock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.insock.connect((HOSTNAME,OUT_PORT))
        self.insock.setblocking(0)
        self.in_fileno = self.insock.fileno()
        print 'input connection'
    
    def handle_write(self):
        if self.out_messages:
            messages = EOL.join(self.out_messages) + EOL
            self.out_messages = []
            print 'sending message', messages
            self.outsock.send(messages)
            
    
    def put_message(self, message):
        print 'put_message', message
        self.out_messages.append(message)
    
    def handle_read(self):
        try:
            data = self.insock.recv(1024)
        except socket.error, err:
            print 'socket.error', err
            if err[0]!=11:
                raise err
            else:
                return []
        else:
            messages = []
            #print 'handle_read', data
            for char in data:
                if char!=EOL:
                    self.buff+=char
                else:
                    messages.append(self.buff)
                    self.buff=''
            for message in messages:
                if not self.accept_message:
                    self.accept_(message)
                else:
                    self.receive(message)

    def loop(self):
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
       
        
    def close_conn(self):
        self.insock.close()
        self.outsock.close()
        
    def handle_close(self):
        print 'connection closed'
    def handle_error(self, Error):
        print Error
        sys.exit()
    
class Client(SelectClient):
    def __init__(self):
        SelectClient.__init__(self)
        self.accept_message = False
        self.in_messages = []
        self.out_messages = []
    
    def wait_for_accept(self):
        print 'waiting for accept'
        self.loop()
        if self.accept_message:
            print 'accepted'
            return self.accept_message
        else:
            return False
    
    def accept_(self, message):
        self.accept_message = unpack_server_accept(message)
        
    def send(self, vector):
        message = pack_client_message(vector)
        self.put_message(message)
        
    
    def receive(self, message):
        #print 'client.receive', message
        move_vector, land, objects, objects_updates = unpack_server_message(message)
        self.in_messages.append((move_vector, land, objects, objects_updates))
              
    

    
def main():
	c = Client()
	return 0

if __name__ == '__main__':
	main()

