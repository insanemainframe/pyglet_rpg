#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, socket, select

from config import HOSTNAME, IN_PORT, OUT_PORT
from engine import *
from protocol import *

EOL = '\n'


class EpollServer:
    def __init__(self, host=HOSTNAME):
        self.inpoll = select.epoll()
        self.insock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.insock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.insock.setblocking(0)
        self.insock.bind((host,IN_PORT))
        self.in_fileno = self.insock.fileno()
        self.inpoll.register(self.in_fileno, select.EPOLLIN)
        
        self.outpoll = select.epoll()
        self.outsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.outsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.outsock.setblocking(0)
        self.outsock.bind((host,OUT_PORT))
        self.out_fileno = self.outsock.fileno()
        self.outpoll.register(self.out_fileno, select.EPOLLIN)
        
        self.address_buf = {}
        self.address_list = []
        self.insocks = {}
        self.outsocks = {}
        self.clients = {}
        self.responses = {}
        self.requests = {}
        self.buffers = {}
        
        self.log = open('/tmp/game.log','w')
        self.log.write('new\n')
    
    def put_messages(self, fileno, message):
        print 'put_message', type(message), len(message)
        self.responses[fileno].append(message)
        self.outpoll.modify(fileno, select.EPOLLOUT)
    
    def handle_write(self, fileno):
        print 'handle_write from', fileno
        if self.responses[fileno]:
            response = (EOL.join(self.responses[fileno])+EOL)
            print('Sending', str(response) if len(response)<100 else type(response), len(response),'to', fileno)
            self.responses[fileno] = []
            self.outsocks[fileno].send(response)
        self.inpoll.modify(fileno, select.EPOLLIN)
    
    def handle_read(self, fileno):
        print 'handle_read from', fileno
        data = self.insocks[fileno].recv(1024)
        messages = []
        for char in data:
            if char!=EOL[0]:
                self.buffers[fileno].append(char)
            else:
                messages.append(''.join(self.buffers[fileno]))
                self.buffers[fileno]=[]
        messages = [message for message in self.read_data(messages, fileno)]
        for key in self.responses:
            self.responses[key].extend(messages)
            self.outpoll.modify(key, select.EPOLLOUT)
        
        self.close_data(fileno)
    
    def handle_accept_in(self):
        conn, (address, fileno) = self.insock.accept()
        conn.setblocking(0)
        fileno = conn.fileno()
        self.insocks[fileno] = conn
        print('input Connection from %s (%s)' % (fileno, address))
        self.address_buf[address] = fileno
        self.inpoll.register(fileno, select.EPOLLIN)
        
    def handle_accept_out(self):
        conn, (address, fileno) = self.outsock.accept()
        conn.setblocking(0)
        out_fileno = conn.fileno()
        self.outsocks[out_fileno] = conn
        in_fileno = self.address_buf[address]
        del self.address_buf[address]
        self.outpoll.register(out_fileno, select.EPOLLOUT)
        print('output Connection from %s (%s)' % (fileno, address))
        self.accept_client(address, in_fileno, out_fileno)
    
    def accept_client(self, address, in_fileno, out_fileno):
        print 'accepting_client', address
        counter = 0
        for exist_address in self.address_list:
            if address not in exist_address:
                counter+=1
        address = address + str(counter)
        
        self.clients[address] = (in_fileno, out_fileno)
        self.requests[in_fileno] = []
        self.responses[out_fileno] = []
        self.in_buffer[in_fileno] = []
        self.out_buffer[out_fileno] = []
        #реагируем на появление нового клиента
        self.accept_data(in_fileno)
    
    def get_name(self, fileno):
        for address, filenos in self.clients.items():
            if fileno in filenos:
                return address

    def handle_in(self, fileno ,event):
        try:
            if fileno==self.in_fileno:
                self.handle_accept_in()
            elif event & select.EPOLLHUP: 
                self.handle_close(fileno)
            elif (event & select.EPOLLIN): 
                self.handle_read(fileno)
            
        except socket.error as Error:
            self.handle_error(Error, fileno, event)
    def handle_out(self, fileno ,event):
        try:
            if fileno==self.out_fileno:
                self.handle_accept_out()
            elif event & select.EPOLLHUP: 
                self.handle_close(fileno)
            elif (event & select.EPOLLOUT):
                self.handle_write(fileno)
        except socket.error as Error:
            self.handle_error(Error, fileno, event)
    
    def run(self):
        self.insock.listen(10)
        self.outsock.listen(10)
        try:
            while 1:
                print 'waiting for INevents'
                inevents = self.inpoll.poll()
                for fileno, event in inevents:
                    self.handle_in(fileno, event)
                print 'waiting for OUTevents'
                outevents = self.outpoll.poll()
                for fileno, event in outevents:
                    self.handle_out(fileno, event)
                    
                
                
        finally:
            self.stop()
    
    def handle_close(self, fileno):
        print('Closing %s' % fileno)
        print ('Responses', self.responses[fileno] )
        self.epoll.unregister(fileno)
        self.clients[fileno].close()
        del self.clients[fileno]
        del self.requests[fileno]
        del self.responses[fileno]
        del self.buffers[fileno]
    
    def handle_error(self, error, *args):
        self.log.write(str(error) + '\n')
    
    def stop(self):
        self.inpoll.unregister(self.in_fileno)
        self.outpoll.unregister(self.out_fileno)
        self.inpoll.close()
        self.outpoll.close()
        self.insock.close()
        self.outsock.close()
        self.log.close()
        print('Stopped')

class GameServer(EpollServer):
    def __init__(self):
        EpollServer.__init__(self)
        self.game = Game(16)
        self.player_list = []
        
    def accept_data(self, fileno):
        "вызывается при подключении клиента"
        message = pack_server_accept(*self.game.accept())
        print 'accept_data', type(message), len(message)
        self.put_messages(fileno, message)


    def read_data(self, messages, fileno):
        print 'read_data', messages
        data = pack_server_message(*self.game.look())
        result = [data]
        return result

    
    def close_data(self, fileno):
        print 'close_data'
        for name in self.clients:
            self.put_messages(name, '')

def main():
    server = GameServer()
    server.run()
    return 0

if __name__ == '__main__':
    main()

