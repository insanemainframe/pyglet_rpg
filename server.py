#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, socket, select
from collections import namedtuple

from config import HOSTNAME, IN_PORT, OUT_PORT
from engine_lib import *
from protocol_lib import *

EOL = '\n'
IN, OUT = 0,1
fileno_tuple = namedtuple('fileno_tuple',('in_','out_'))

class FilenoError(Exception):
    def __init__(self, fileno, text = ''):
        self.fileno = fileno
        Exception.__init__(self, '%s %s' % (fileno,text))

class HandleAcceptError(Exception):
    pass
        

class EpollServer:
    def __init__(self, host=HOSTNAME, listen_num=10):
        self.poll = select.epoll()
        self.listen_num = listen_num
        
        self.insock, self.in_fileno = self.create_socket(host, IN_PORT)
        self.outsock, self.out_fileno = self.create_socket(host, OUT_PORT)
        
        
        self.address_buf = {}
        self.address_list = []
        self.insocks = {}
        self.outsocks = {}
        self.clients = {}
        self.responses = {}
        self.requests = {}
        self.in_buffers = {}
        self.out_buffers = {}
        
        self.counter = 0
        
        self.log = open('/tmp/game.log','w')
    
    def create_socket(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(0)
        sock.bind((host, port))
        fileno = sock.fileno()
        self.poll.register(fileno, select.EPOLLIN)
        return sock, fileno
    
    def put_message(self, address, message):
        print 'put_message', str(message) if len(message)<50 else type(message), len(message)
        self.responses[address].append(message)
        out_fileno = self.clients[address].out_
        self.poll.modify(out_fileno, select.EPOLLOUT)
    
    def handle_write(self, fileno):
        address = self.get_address(fileno)
        fileno = self.clients[address].out_
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
        #print 'handle_read ', 'buffer'+''.join(self.in_buffers[address]) if len(messages)<20 else type(messages), len(messages)
        self.read(messages, address)
        

    
    def handle_accept(self, stream):
        
        if stream==IN:
            conn, (address, in_fileno) = self.insock.accept()
            in_fileno = conn.fileno()
            self.insocks[in_fileno] = conn
            fileno = in_fileno
            print('input Connection from %s (%s)' % (in_fileno, address))
        elif stream==OUT:
            conn, (address, out_fileno) = self.outsock.accept()
            out_fileno = conn.fileno()
            self.outsocks[out_fileno] = conn
            fileno = out_fileno
            print('output Connection from %s (%s)' % (out_fileno, address))
        else:
            raise HandleAcceptError('unknnowsn stream %s' % stream)
        
        conn.setblocking(0)
        
        if address not in self.address_buf:
            self.address_buf[address] = fileno
        else:
            if stream==IN:
                out_fileno = self.address_buf[address]
            else:
                in_fileno = self.address_buf[address]
            del self.address_buf[address]
            self.accept_client(address, in_fileno, out_fileno)
        
    
    def accept_client(self, address, in_fileno, out_fileno):
        address = address + str(self.counter)
        self.counter+=1
        print 'accepting_client', address
        
        self.clients[address] = fileno_tuple(in_fileno, out_fileno)
        self.requests[address] = []
        self.responses[address] = []
        self.in_buffers[address] = []
        self.out_buffers[address] = []
        #регистрируем
        self.poll.register(in_fileno, select.EPOLLIN)
        self.poll.register(out_fileno, select.EPOLLOUT)
        #реагируем на появление нового клиента
        self.accept(address)
    
  

    
    def get_address(self, fileno):
        for address, filenos in self.clients.items():
            if fileno in filenos:
                return address
        raise FilenoError(fileno, 'FilenoError')
    
    def has_reponse(self, fileno):
        address = self.get_address(fileno)
        return bool(self.responses[address])

    def run(self):
        self.insock.listen(self.listen_num)
        self.outsock.listen(self.listen_num)
        try:
            while 1:
                events = self.poll.poll()
                for fileno, event in events:
                    try:
                        if fileno==self.in_fileno:
                            print 'self.handle_accept_in(%s)' % fileno
                            self.handle_accept(IN)
                        elif fileno==self.out_fileno:
                            print 'self.handle_accept_out(%s)' % fileno
                            self.handle_accept(OUT)
                        elif (event & select.EPOLLIN): 
                            print 'self.handle_read(%s)' % fileno
                            self.handle_read(fileno)
                        elif (event & select.EPOLLOUT) and self.has_reponse(fileno):
                            print 'self.handle_write(%s) %s' % (fileno, str( self.responses))
                            self.handle_write(fileno)
                        elif event & select.EPOLLHUP: 
                            print 'self.handle_close(%s)' % fileno
                            self.handle_close(fileno)
                    except socket.error as Error:
                        self.handle_error(Error, fileno, event)
                    except FilenoError, excp:
                        print excp
                        self.handle_close(excp.fileno)
        finally:
            self.stop()
    
    def handle_close(self, fileno):
        try:
            address = self.get_address(fileno)
        except FilenoError:
            print 'handle_close fileno_error %s with %s' % (fileno, str(self.clients))
        else:
            in_fileno, out_fileno = self.clients[address]
            
            self.poll.unregister(in_fileno)
            self.poll.unregister(out_fileno)
            print 'unregister', in_fileno, out_fileno
            
            self.insocks[in_fileno].close()
            del self.insocks[in_fileno]
            self.outsocks[out_fileno].close()
            del self.outsocks[out_fileno]
            
            del self.clients[address]
            del self.requests[address]
            del self.responses[address]
            del self.in_buffers[address]
            del self.out_buffers[address]
            try:
                self.address_list.remove(address)
            except ValueError:
                pass
        
            self.close(address)
            print('Closing %s(%s,%s)' % (address, in_fileno, out_fileno))
    
    def handle_error(self, error, fileno, event):
        self.handle_close(fileno)
        self.log.write(str(fileno, event) + '\n')
    
    def stop(self):
        self.poll.unregister(self.in_fileno)
        self.poll.unregister(self.out_fileno)
        self.poll.close()
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
        self.games = {}
        self.player_list = []
        
    def accept(self, address):
        "вызывается при подключении клиента"
        self.games[address] = Game(16)
        message = pack_server_accept(*self.games[address].accept())
        print 'accept_data', type(message), len(message)
        self.put_message(address, message)


    def read(self, messages, address):
        for message in messages:
            vector = unpack_client_message(message)
            self.games[address].go(vector)
            data = pack_server_message(*self.games[address].look())
            print 'read_data', message, '->', data
            self.put_message(address, data)

    
    def close(self, address):
        del self.games[address]
        print 'closing game', address

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

