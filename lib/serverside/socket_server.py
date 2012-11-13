#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import IN_PORT, OUT_PORT, SOCKET_SERVER_PROFILE, SOCKET_SERVER_PROFILE_FILE

import cProfile
import socket
from sys import exc_info, exit as sys_exit
import traceback
from threading import Thread
from multiprocessing import Process, Queue, Event
from collections import namedtuple
from socket import error as socket_error


from share.protocol_lib import send, receivable, PackageError
from serverside.multiplexer import Multiplexer
from share.logger import print_log



IN, OUT = 0, 1
PORTS = {IN: IN_PORT, OUT: OUT_PORT}


class HandleAcceptError(BaseException):
    pass


client_tuple = namedtuple('client_tuple', ('insock', 'outsock', 'generator'))


class SocketServer(Multiplexer, Process):
    "получает/отправляет данные через сокеты"
    def __init__(self, hostname, listen_num=100):
        Process.__init__(self)
        Multiplexer.__init__(self)
        self.listen_num = listen_num
        self.hostname = hostname

        self.insock, self.in_fileno = self._create_socket(IN)
        self.outsock, self.out_fileno = self._create_socket(OUT)

        self.infilenos = {}
        self.insocks = {}
        self.outfilenos = {}

        self._address_buf = {}

        self._accepted = Queue()
        self._closed = Queue()
        self._requestes = Queue()
        self._responses = Queue()
        self.excp = Queue()

        self._sender_thread  = Thread(target = self._sender)

        self.clients = {}
        self.client_counter = 0

        self._stop_event = Event()
                
        
        self.r_times = []
        self.running = False


    #публичные методы
    def get_accepted(self):
        while not self._accepted.empty():
            yield self._accepted.get_nowait()
        raise StopIteration

    def get_closed(self):
        while not self._closed.empty():
            yield self._closed.get_nowait()
        raise StopIteration

    def get_requestes(self):
        while not self._requestes.empty():
            client, request = self._requestes.get_nowait()
            yield client, request
        raise StopIteration

    def put_response(self, client_name, response):
        self._responses.put_nowait((client_name, response))



    def _handle_exception(self, except_type, except_class, tb):
        try:
            self.excp.put_nowait((except_type, except_class, traceback.extract_tb(tb)))
        finally:
            self.stop()
            
    def _create_socket(self, stream):
        "создает неблокирубщий сокет на заданном порте"
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.hostname, PORTS[stream]))
        sock.setblocking(0)
        fileno = sock.fileno()
        return sock, fileno

    def _sender(self):
        try:
            while not self._stop_event.is_set():
                client_name, response = self._responses.get()
                if client_name in self.clients:
                    sock = self.clients[client_name].outsock
                    try:
                        send(sock, response)
                    except socket_error as error:
                        print_log('sender error', str(error))
            print_log('sender stop')

        except Exception as error:
            print_log ('snder', error)
            self._handle_exception(*exc_info())

            

    
    def _handle_read(self, client_name):
        "читает один пакет данных из сокета, если это возможно"
        try:
            request = self.clients[client_name].generator.next()

        except socket.error as Error:
            #если возникла ошабка на сокете - закрываем"
            errno = Error[0]
            self._handle_close(client_name, 'Socket Error %s' % errno)
            return False
                            
        except PackageError:
            #если возникла ошабка в пакете - закрываем"
            self._handle_close(client_name, 'PackageError')
            return False
            
        except StopIteration:
            #если клиент отключился"
            self._handle_close(client_name, 'Disconnect')
            return False
        else:
            if request:
                self._requestes.put_nowait((client_name, request))
            return True
            
        
    def _handle_accept(self, stream):
        "прием одного из двух соединений"
        assert stream in (IN, OUT)

        if stream is IN:
            sock = self.insock
            s_name = 'input'

        else:
            sock = self.outsock
            s_name = 'output'

        conn, (address, fileno) = sock.accept()
        conn.setblocking(0)

        print_log ('%s Connection from %s (%s)' % (s_name, fileno, address))
        
        
        
        if address not in self._address_buf:
            self._address_buf[address] = conn
        else:
            buf_address = self._address_buf.pop(address)

            if stream==IN:
                self._accept_client(conn, buf_address)

            else:
                 outsock = conn
                 self._accept_client(buf_address, conn)
                 
            
                             
    def _accept_client(self, insock, outsock):
        "регистрация клиента, после того как он подключился к обоим сокетам"
        client_name = 'player_%s' % self.client_counter
        self.client_counter+=1
        
        self.clients[client_name] = client_tuple(insock,outsock, receivable(insock))
        
        insock_fileno = insock.fileno()
        outsock_fileno = outsock.fileno()
        
        self.infilenos[insock_fileno] = client_name
        self.outfilenos[outsock_fileno] = client_name
        
        
        self._register_in(insock_fileno)

        
        print_log('accepting_client %s' % client_name)

        #реагируем на появление нового клиента
        self._accepted.put_nowait(client_name)
        
    

    
    def run(self):
        try:
            if SOCKET_SERVER_PROFILE:
                cProfile.runctx('self._run()', globals(),locals(),SOCKET_SERVER_PROFILE_FILE)
            else:
                self._run()
        finally:
            self.stop()

    def _run(self):
        self.running = True

        self.insock.listen(self.listen_num)
        self.outsock.listen(self.listen_num)
        
        #регистрируем сокеты на ожидание подключений
        self._register_in(self.insock.fileno())
        self._register_in(self.outsock.fileno())
        

        
       
        print_log('\nServer running at %s:(%s,%s) multiplexer: %s \n' % (self.hostname, IN_PORT, OUT_PORT, self.poll_engine))
        try:
            #запускаем sender
            self._sender_thread.start()
        
            #запускаем мультиплексор
            self._run_poll()
        except:
            self._handle_exception(*exc_info())

        finally:
            self.stop()


    
    def _handle_close(self, client_name, message):
        "закрытие подключения"
        print_log('Closing %s: %s' % (client_name, message))
        
        self._closed.put_nowait(client_name)
        
        #
        infileno = self.clients[client_name].insock.fileno()
        outfileno = self.clients[client_name].outsock.fileno()
        
        self._unregister(infileno)
        
        
        
        del self.infilenos[infileno]
        del self.outfilenos[outfileno]
        
        #закрываем подключения и удаляем
        
        self.clients[client_name].insock.close()
        self.clients[client_name].outsock.close()
        del self.clients[client_name]

        
    
    def stop(self, reason=None):
        if self.running:
            print_log('SocketServer stopping..')

            self._unregister(self.in_fileno)
            self._unregister(self.out_fileno)
                
            self.insock.close()
            self.outsock.close()


            self._stop_event.set() 


            #closing queues
            self._accepted.close()
            self._closed.close()
            self._requestes.close()
            self._responses.close()



            print_log ('Waiting for sender thread')
            self._sender_thread._Thread__stop()
            self._sender_thread.join()

            self.running = False


            
        
    
    

        


