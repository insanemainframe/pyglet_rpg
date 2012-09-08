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
        self.in_buffers = {}
        self.out_buffers = {}
        
        self.log = open('/tmp/game.log','w')
        self.log.write('new\n')
    
    def put_message(self, address, message):
        print 'put_message', str(message) if len(message)<50 else type(message), len(message)
        self.responses[address].append(message)
        out_fileno = self.get_fileno(address)[1]
        self.outpoll.modify(out_fileno, select.EPOLLOUT)
    
    def handle_write(self, fileno):
        address = self.get_address(fileno)
        print 'handle_write from', address
        fileno = self.get_fileno(address)[1]
        if self.responses[address]:
            response = (EOL.join(self.responses[address])+EOL)
            print('Sending', str(response) if len(response)<50 else type(response), len(response),'to', fileno)
            self.responses[address] = []
            self.outsocks[fileno].send(response)
    
    def handle_read(self, fileno):
        address = self.get_address(fileno)
        data = self.insocks[fileno].recv(1024)
        messages = []
        for char in data:
            if char!=EOL[0]:
                self.in_buffers[address].append(char)
            else:
                messages.append(''.join(self.in_buffers[address]))
                self.in_buffers[address] = []
        print 'handle_read ', 'buffer'+''.join(self.in_buffers[address]) if len(messages)<20 else type(messages), len(messages)
        self.read_data(messages, address)
        

    
    def handle_accept_in(self):
        conn, (address, in_fileno) = self.insock.accept()
        print('input Connection from %s (%s)' % (in_fileno, address))
        conn.setblocking(0)
        in_fileno = conn.fileno()
        self.insocks[in_fileno] = conn
        
        if address not in self.address_buf:
            self.address_buf[address] = in_fileno
        else:
            out_fileno = self.address_buf[address]
            del self.address_buf[address]
            self.accept_client(address, in_fileno, out_fileno)
        
    def handle_accept_out(self):
        conn, (address, out_fileno) = self.outsock.accept()
        print('output Connection from %s (%s)' % (out_fileno, address))
        conn.setblocking(0)
        out_fileno = conn.fileno()
        self.outsocks[out_fileno] = conn
        if address not in self.address_buf:
            self.address_buf[address] = out_fileno
        else:
            in_fileno = self.address_buf[address]
            del self.address_buf[address]
            self.accept_client(address, in_fileno, out_fileno)
    
    def accept_client(self, address, in_fileno, out_fileno):
        print 'accepting_client', address
        counter = 0
        for exist_address in self.address_list:
            if address not in exist_address:
                counter+=1
        address = address + str(counter)
        
        self.clients[address] = (in_fileno, out_fileno)
        self.requests[address] = []
        self.responses[address] = []
        self.in_buffers[address] = []
        self.out_buffers[address] = []
        #регистрируем
        self.inpoll.register(in_fileno, select.EPOLLIN)
        self.outpoll.register(out_fileno, select.EPOLLOUT)
        #реагируем на появление нового клиента
        self.accept_data(address)
    
    def get_fileno(self, address):
        return self.clients[address]

    
    def get_address(self, fileno):
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
                print 'waiting for OUTevents'
                outevents = self.outpoll.poll()
                for fileno, event in outevents:
                    self.handle_out(fileno, event)
                print 'waiting for INevents'
                inevents = self.inpoll.poll()
                for fileno, event in inevents:
                    self.handle_in(fileno, event)
                
                    
                
                
        finally:
            self.stop()
    
    def handle_close(self, fileno):
        print('Closing %s' % fileno)
        address = self.get_address(fileno)
        print ('Responses', self.responses[address] )
        
        in_fileno, out_fileno = self.get_fileno(address)
        
        self.insocks[in_fileno].close()
        del self.insocks[in_fileno]
        self.outsocks[out_fileno].close()
        del self.outsocks[out_fileno]
        
        del self.clients[address]
        del self.requests[address]
        del self.responses[address]
        del self.in_buffers[address]
        del self.out_buffers[address]
    
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
        if PROFILE:
            print 'profile'
            stats = pstats.Stats('/tmp/server_pyglet.stat')
            stats.sort_stats('cumulative')
            stats.print_stats()

class GameServer(EpollServer):
    def __init__(self):
        EpollServer.__init__(self)
        self.game = Game(16)
        self.player_list = []
        
    def accept_data(self, address):
        "вызывается при подключении клиента"
        message = pack_server_accept(*self.game.accept())
        print 'accept_data', type(message), len(message)
        self.put_message(address, message)


    def read_data(self, messages, address):
        for message in messages:
            vector = unpack_client_message(message)
            self.game.go(vector)
            data = pack_server_message(*self.game.look())
            print 'read_data', message, '->', data
            self.put_message(address, data)

    
    def close_data(self, address):
        print 'close_data'
        for name in self.clients:
            self.put_messages(name, '')

def main():
    server = GameServer()
    server.run()

if __name__ == '__main__':
    PROFILE = 0
    if PROFILE:
        import cProfile, pstats
        cProfile.run('main()', '/tmp/server_pyglet.stat')

    else:
        main()

