#!/usr/bin/env python
# -*- coding: utf-8 -*-
#SOCKET LAYER
from sys import path; path.append('../')

import socket
from time import time

from poll_lib import PollServer
from share.protocol_lib import send, receivable, PackageError
from config import IN_PORT, OUT_PORT, SERVER_TIMER, PROFILE_SERVER


IN, OUT = 0,1
PORTS = {IN:IN_PORT, OUT:OUT_PORT}

class HandleAcceptError(Exception):
    pass

class SocketError:
    def __init__(self, error):
        self.error = error
    def __str__(self):
        return 'SocketError: %s' %self.error

#####################################################################
class SocketServer(PollServer):
    "получает/отправляет данные через сокеты"
    def __init__(self, timer_value=SERVER_TIMER, listen_num=10):
        PollServer.__init__(self)
        self.listen_num = listen_num
        self.timer_value = timer_value
        
        self.insock, self.in_fileno = self.create_socket(IN)
        self.outsock, self.out_fileno = self.create_socket(OUT)
        self.insocks, self.outsocks = {}, {}
        
        self.generators = {}
        
        self.address_buf = {}
        
        self.responses = {}
        self.requests = {}
        
        self.client_counter = 0
            
    def create_socket(self, stream):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(0)
        sock.bind((self.hostname, PORTS[stream]))
        fileno = sock.fileno()
        self.register_accept(fileno, stream)
        return sock, fileno
    
    def put_messages(self, address, messages):
        self.responses[address]+=messages
    
    def handle_write(self):
        if self.responses:
            for address in self.responses:
                responses = self.responses[address]
                for response in responses:
                    self.send(address, response)
                self.responses[address] = []
    
    def handle_read(self, address):
        try:
            message = self.generators[address].next()
        except socket.error as Error:
            print 'handle read socket error %s' % Error
            errno = Error[0]
            if Error[0]==104:
                self.handle_close(address)
                return False
            return True
        
        except PackageError:
            print 'PackageError'
            self.handle_close(address)
            return False
            
        except StopIteration:
            self.handle_close(address)
            return False
            
        else:
            if message:
                self.read(address, [message])
            return True
            
            
        
    def handle_accept(self, stream):
        "прием одного из двух соединений"
        if stream==IN:
            conn, (address, fileno) = self.insock.accept()
            conn.setblocking(0)
            print('input Connection from %s (%s)' % (fileno, address))
            
        elif stream==OUT:
            conn, (address, fileno) = self.outsock.accept()
            conn.setblocking(0)
            print('output Connection from %s (%s)' % (fileno, address))
        else:
            raise HandleAcceptError('unknnowsn stream %s' % stream)
        
        conn.setblocking(0)
        
        if address not in self.address_buf:
            self.address_buf[address] = conn
            return True
        else:
            if stream==IN:
                insock = conn
                outsock = self.address_buf[address]
                
            else:
                 outsock = conn
                 insock = self.address_buf[address]
                 
            del self.address_buf[address]
            infileno = insock.fileno()
            return self.accept_client(infileno, address,insock, outsock)   
                 
    def accept_client(self, fileno, sock_address, insock, outsock):
        "регистрация клиента, после того как он подключился к обоим сокетам"
        address = 'plaayer_%s' % self.client_counter
        self.client_counter+=1
        self.insocks[address] = insock
        self.generators[address] = receivable(insock)
        self.outsocks[address] = outsock
        in_fileno, out_fileno = self.insocks[address].fileno(), self.outsocks[address].fileno()
        
        self.requests[address] = []
        self.responses[address] = []
        
        print 'accepting_client %s' % address
        #регистрируем
        self.register_read(in_fileno, address)
        self.register(address, in_fileno, out_fileno)
        #реагируем на появление нового клиента
        self.accept(address)
        return True

    def run(self):
        print 'Server running at %s:(%s,%s) with %s' % (self.hostname, IN_PORT, OUT_PORT, self.poll_engine)
        self.insock.listen(self.listen_num)
        self.outsock.listen(self.listen_num)
        try:
            self.run_poll()
        finally:
            self.stop()
    
    def handle_close(self, address):
        print 'Closing %s' % address
        self.close(address)
        
        in_fileno, out_fileno = self.insocks[address].fileno(), self.outsocks[address].fileno()
        
        self.insocks[address].close()
        del self.insocks[address]
        self.outsocks[address].close()
        del self.outsocks[address]
        
        del self.requests[address]
        del self.responses[address]
       
        return self.unregister(address, in_fileno, out_fileno)
    
    def handle_error(self, error, address):
        print '%s handle error %s' % (address, error)
        self.handle_close(address)
    
    def stop(self):
        self.stop_poll()
        self.insock.close()
        self.outsock.close()
        print('Stopped')
        if PROFILE_SERVER:
            import pstats
            print 'profile'
            stats = pstats.Stats('/tmp/game_server.stat')
            stats.sort_stats('cumulative')
            stats.print_stats()
    
    def send(self, address, data):
        sock = self.outsocks[address]
        send(sock,data)
        
    def receive(self, address):
        sock = sock = self.insocks[address]
        return receive(sock)


