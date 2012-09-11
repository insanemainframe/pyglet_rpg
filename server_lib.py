#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket, thread

from time import sleep, time
from select import epoll, EPOLLIN, EPOLLOUT
from collections import namedtuple


from config import HOSTNAME, IN_PORT, OUT_PORT, SERVER_TIMER, PROFILE, EOL


IN, OUT = 0,1
fileno_tuple = namedtuple('fileno_tuple',('in_','out_'))

class FilenoError(Exception):
    def __init__(self, fileno, text = ''):
        self.fileno = fileno
        Exception.__init__(self, '%s %s' % (fileno,text))

class HandleAcceptError(Exception):
    pass
        
class TimerCallable:
    def __init__(self, timer_value=SERVER_TIMER):
        self.timer_value = timer_value
        
    def start_timer(self):
        thread.start_new_thread(self.timer_thread,())
        
    def timer_thread(self):
        while 1:
            sleep(self.timer_value)
            try:
                self.timer_handler()
            except Exception, exception:
                print exception
        

class EpollServer:
    def __init__(self, listen_num=10):
        
        self.poll = epoll()
        self.listen_num = listen_num
        
        self.insock, self.in_fileno = self.create_socket(IN_PORT)
        self.outsock, self.out_fileno = self.create_socket(OUT_PORT)
        self.insocks, self.outsocks = {}, {}
        self.in_buffers, self.out_buffers = {}, {}
        
        
        self.address_buf = {}
        self.address_list = []
        
        self.clients = {}
        self.responses = {}
        self.requests = {}
            
    def create_socket(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(0)
        sock.bind((self.hostname, port))
        fileno = sock.fileno()
        self.poll.register(fileno, EPOLLIN)
        return sock, fileno
    
    def put_message(self, address, message):
        self.responses[address].append(message)
        out_fileno = self.clients[address].out_
        self.poll.modify(out_fileno, EPOLLOUT)
    
    def has_responses(self):
        for response in self.responses.values():
            if response:
                return True
        return False
    
    def handle_write(self, fileno):
        address = self.get_address(fileno)
        self.write(address)
        if not self.responses[address]:
            return 
        fileno = self.clients[address].out_
        if self.responses[address]:
            response = (EOL.join(self.responses[address])+EOL)
            self.responses[address] = []
            self.outsocks[fileno].send(response)
    
    def handle_read(self, fileno):
        address = self.get_address(fileno)
        data = self.insocks[fileno].recv(1024)
        if not data:
            self.handle_close(address)
        messages = []
        for char in data:
            if char!=EOL[0]:
                self.in_buffers[address].append(char)
            else:
                messages.append(''.join(self.in_buffers[address]))
                self.in_buffers[address] = []
        self.read(address, messages)
        

    
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
        address = str(abs(hash((address, time()))))
        self.clients[address] = fileno_tuple(in_fileno, out_fileno)
        
        print 'accepting_client %s %s' % ( self.get_address(in_fileno), self.clients[address])
        
        
        self.requests[address] = []
        self.responses[address] = []
        self.in_buffers[address] = []
        self.out_buffers[address] = []
        #регистрируем
        self.poll.register(in_fileno, EPOLLIN)
        self.poll.register(out_fileno, EPOLLOUT)
        #реагируем на появление нового клиента
        self.accept(address)


    
    def get_address(self, fileno):
        for address, filenos in self.clients.items():
            if fileno in filenos:
                return address
        raise FilenoError(fileno, 'FilenoError')
    

    def run(self):
        print 'Server running at %s:(%s,%s)' % (HOSTNAME, IN_PORT, OUT_PORT)
        self.insock.listen(self.listen_num)
        self.outsock.listen(self.listen_num)
        try:
            while 1:
                events = self.poll.poll()
                for fileno, event in events:
                    try:
                        if fileno==self.in_fileno:
                            self.handle_accept(IN)
                        elif fileno==self.out_fileno:
                            self.handle_accept(OUT)
                        elif event==EPOLLIN: 
                            self.handle_read(fileno)
                        elif self.has_responses and event==EPOLLOUT:
                            self.handle_write(fileno)
                    except socket.error as Error:
                        self.handle_error(Error, fileno, event)
        finally:
            self.stop()
    
    def handle_close(self, address):
        self.close(address)
        in_fileno, out_fileno = self.clients[address]
        
        self.poll.unregister(in_fileno)
        self.poll.unregister(out_fileno)
        
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
    
        
        print('Closing %s(%s,%s)' % (address, in_fileno, out_fileno))
    
    def handle_error(self, error, fileno, event):
        print '%s error %s' % (fileo, error)
        self.handle_close(fileno)
    
    def stop(self):
        self.poll.unregister(self.in_fileno)
        self.poll.unregister(self.out_fileno)
        self.poll.close()
        self.insock.close()
        self.outsock.close()
        print('Stopped')
        if PROFILE:
            import pstats
            print 'profile'
            stats = pstats.Stats('/tmp/game_server.stat')
            stats.sort_stats('cumulative')
            stats.print_stats()

