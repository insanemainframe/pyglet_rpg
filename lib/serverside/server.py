#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import SERVER_TIMER, HOSTNAME, PROFILE_SERVER, SERVER_PROFILE_FILE

from sys import exit as sys_exit, exc_info
import traceback
import cProfile
from time import time, sleep
from collections import defaultdict

from engine.engine_interface import GameEngine

from share.packer import pack, unpack
from serverside.socket_server import SocketServer
from share.logger import print_log


class GameServer(object):
    "игровой сервер"

    def __init__(self, hostname, save_time=600):
        self.server = SocketServer(hostname)

        self.client_list = set()
        self.client_requestes = defaultdict(list)
        
        #сам игровой движок
        self.game = GameEngine(save_time)
        
        self.round_counter = 0
        self.r_times = []
            
    def game_worker(self):
        "передает запросы, новых/отключившихся клиентов движку, и получает запросы"
        #смотрим новых клиентов
        for client_name in self.server.get_accepted():
            self.client_list.add(client_name)
            for response in self.game.game_connect(client_name):
                accept_response = pack(response)
                self.server.put_response(client_name, accept_response)

        #смотрим отключившихся клиентов
        for client_name in self.server.get_closed():
            self.game.game_quit(client_name)

            self.client_list.remove(client_name)

        #смотрим новые запросы и очищаем очередь
        requestes = list(self.server.get_requestes())

        for client_name, message in requestes:
            self.client_requestes[client_name].append(unpack(message))

        #отправляем запросы движку
        self.game.game_requests(self.client_requestes)

        self.client_requestes.clear()
        
        #обновляем движок
        self.game.game_update()
        
        #вставляем ответы в очередь на отправку
        for client_name, messages in self.game.game_responses():
            for message in messages:
                response = pack(message)
                self.server.put_response(client_name, response)
        
        #завершаем раунд игры
        self.game.end_round()

    def stop(self, stop_reason=''):
        "остановка всего сервера"
        #считаем среднее время на раунд
        print_log('%s \n GameServer stopping...' % str(stop_reason))

        try:
            self.server.stop()
        finally:
            count = len(self.r_times)
            if count:
                all_time = sum(self.r_times)
                m_time = all_time / count
                print_log('median time %s/%s = %s' % (all_time, count, m_time))

            if isinstance(stop_reason, BaseException):
                raise stop_reason
    
    def start(self):
        print_log('Running...')
        stop_reason = 'None'
        try:
            self.server.start()
            print_log('GameServer running')
            t = time()
            while 1:
                if not self.server.excp.empty():
                    print_log('error in SocketServer')
                    stop_reason = self.server.excp.get_nowait()
                    break

                r_time = time()
            
                self.game_worker()
                
                self.r_times.append(time() - r_time)
                
                delta = time() - t
                timeout = SERVER_TIMER - delta if delta < SERVER_TIMER else 0
                t = time()
                sleep(timeout)
            print_log('game loop end')

        except KeyboardInterrupt:
            stop_reason = 'KeyboardInterrupt'
            self.game.save()
            print_log('stop_reason:', stop_reason)

        except:
            except_type, except_class, tb = exc_info()
            print_log('exception!', except_type, except_class)
            for line in traceback.extract_tb(tb):
                print_log(line)

        finally:
            print_log('game loop exit')
         
            self.stop(stop_reason)
            sys_exit()
    

