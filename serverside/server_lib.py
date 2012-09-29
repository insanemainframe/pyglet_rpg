#!/usr/bin/env python
# -*- coding: utf-8 -*-
#SOCKET LAYER
from sys import path; path.append('../')

from config import *

from share.protocol_lib import send, receivable, PackageError
from poll_lib import PollServer

import socket
from time import sleep, time
from threading import Thread, RLock
from collections import namedtuple


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
client_tuple = namedtuple('client_tuple' ,('insock','outsock', 'generator'))

class SocketServer(PollServer):
    "получает/отправляет данные через сокеты"
    def __init__(self, timer_value=SERVER_TIMER, listen_num=100):
        PollServer.__init__(self)
        self.listen_num = listen_num
        
        self.insock, self.in_fileno = self.create_socket(IN)
        self.outsock, self.out_fileno = self.create_socket(OUT)
        
        self.infilenos = {}
        self.insocks = {}
        
        self.address_buf = {}
        
        self.responses = {}
        
        self.clients = {}
        self.client_counter = 0
        self.running = True
        
        self.closed = []
        
        self.server_lock = RLock() 
        self.engine_lock = RLock() #блокровка для действий с движком т.е. game_connect, game_quit
        self.responses_lock = RLock() #блокировка для действий с сокетсервером куызщтыуы куйгууыеуы
            
    def create_socket(self, stream):
        "создает неблокирубщий сокет на заданном порте"
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.hostname, PORTS[stream]))
        sock.setblocking(0)
        if stream==OUT:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) #сразу отправлять клиенту
        fileno = sock.fileno()
        return sock, fileno
    
    def put_messages(self, client_name, messages):
        "добавить ответ в стек"
        with self.responses_lock:
            if client_name in self.responses:
                self.responses[client_name]+=messages
    
    def write_to_all(self):
        "послать ответы всем клиентам"
        
        with self.responses_lock:
            to_write =  self.responses
            self.responses = {client:[] for client in self.responses}
        
        for client_name, responses in to_write.items():
            if responses:
                #print 'write %s' % self.round_n
                if client_name in self.clients:
                    sock = self.clients[client_name].outsock
                    for response in responses:
                        send(sock, response)
                else:
                    #print 'write to closed client'
                    pass
    
    def handle_read(self, client_name):
        "читает один пакет данных из сокета"
        #print '\n handle read'
        try:
            message = self.clients[client_name].generator.next()

        except socket.error as Error:
            #если возникла ошабка на сокете - закрываем"
            errno = Error[0]
            self.handle_close(client_name, 'Socket Error %s' % errno)
            return False
                            
        except PackageError:
            #если возникла ошабка в пакете - закрываем"
            self.handle_close(client_name, 'PackageError')
            return False
            
        except StopIteration:
            #если клиент отключился"
            self.handle_close(client_name, 'Disconnect')
            return False
        else:
            if message:
                self.read(client_name, message)
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
        else:
            if stream==IN:
                insock = conn
                outsock = self.address_buf[address]
                
            else:
                 outsock = conn
                 insock = self.address_buf[address]
                 
            del self.address_buf[address]
            
            self.accept_client(insock, outsock)
        return True
                 
    def accept_client(self, insock, outsock):
        "регистрация клиента, после того как он подключился к обоим сокетам"
        client_name = 'player_%s' % self.client_counter
        self.client_counter+=1
        
        self.clients[client_name] = client_tuple(insock,outsock, receivable(insock))
        
        self.infilenos[insock.fileno()] = client_name
        
        print 'insock.fileno()', insock.fileno()
        self.register(insock.fileno())

        
        with self.responses_lock:
            self.responses[client_name] = []
        
        print 'accepting_client %s' % client_name

        #реагируем на появление нового клиента
        with self.server_lock:
            self.accept(client_name)
        
    def timer_thread(self):
        "отдельный поток для обращения к движку и рассылке ответов"
        t = time()
        while self.running:
            self.timer_handler()
            self.write_to_all()
            delta = time()-t
            timeout = SERVER_TIMER - delta if delta<SERVER_TIMER else 0
            t = time()
            sleep(timeout)

    def run(self):
        print 'Server running at %s:(%s,%s) multiplexor: %s' % (self.hostname, IN_PORT, OUT_PORT, self.poll_engine)
        self.insock.listen(self.listen_num)
        self.outsock.listen(self.listen_num)
        #
        self.register(self.insock.fileno())
        self.register(self.outsock.fileno())
        #
        self.timer_init()
        thread = Thread(target=self.timer_thread)
        thread.start()
        #
        try:
            self.run_poll()
        finally:
            self.stop()
    
    def handle_close(self, client_name, message):
        "закрытие подключения"
        print 'Closing %s: %s' % (client_name, message)
        
        with self.server_lock:
            self.close(client_name)
        
        infileno = self.clients[client_name].insock.fileno()
        
        del self.infilenos[infileno]
        
        self.clients[client_name].insock.close()
        self.clients[client_name].outsock.close()
        del  self.clients[client_name]

        
        with self.responses_lock:
            del self.responses[client_name]
        
    def stop(self):
        "сотановка сервера"
        self.running = False
        #
        self.unregister(self.insock.fileno())
        self.unregister(self.outsock.fileno())
        #
        self.insock.close()
        self.outsock.close()
        print('Stopped')
        if PROFILE_SERVER:
            import pstats
            print 'profile'
            stats = pstats.Stats('/tmp/game_server.stat')
            stats.sort_stats('cumulative')
            stats.print_stats()
    

        


