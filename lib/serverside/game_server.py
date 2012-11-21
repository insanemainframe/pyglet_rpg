#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import SERVER_TIMER, HOSTNAME, PROFILE_SERVER, SERVER_PROFILE_FILE, DEBUG, ACCEPT_NUMBER
from server_logger import debug

from sys import exit as  exc_info
import signal
import traceback
import cProfile
from time import time, sleep
from collections import defaultdict


from engine.engine_interface import GameEngine
from serverside.socket_server import SocketServer




class GameServer(object):
    "игровой сервер"
    def __init__(self, hostname, listen_num = 100, save_time = 600):
        self.server = SocketServer(hostname, listen_num)

        self.client_list = set()    
        self.client_requestes = defaultdict(list)
        
        #сам игровой движок
        self.game = GameEngine(save_time)
        
        self.round_counter = 0
        self.r_times = []
            

    def game_worker(self):
        "обращается к движку по расписанию"
        #смотрим новых клиентов

        blocking = self.game.is_active()
        if blocking:
            debug ('Sleeeping mode')

        for client_name in self.server.get_accepted(blocking = blocking):
            for accept_response in self.game.game_connect(client_name):
                self.server.put_response(client_name, accept_response)

            self.client_list.add(client_name)
        
        #смотрим отключившихся клиентов
        for client_name in self.server.get_closed():
            self.game.game_quit(client_name)

            self.client_list.remove(client_name)

        
        #смотрим новые запросы и очищаем очередь
        
        requestes = list(self.server.get_requestes())


        for client_name, message in requestes:
            self.client_requestes[client_name].append(message)

        
        #отправляем запросы движку
        self.game.game_requests(self.client_requestes)

        self.client_requestes.clear()
        
        #обновляем движок
        self.game.game_update()
        
        #вставляем ответы в очередь на отправку
        for client_name, messages in self.game.game_responses():
            for message in messages:
                self.server.put_response(client_name, message)
        
        #завершаем раунд игры
        self.game.end_round()

    def sigint(self, sig_Num, frame):
        self.stop('server sigint')




    def stop(self, stop_reason = ''):
        #считаем среднее время на раунд
        if self.running:
            self.debug()
            debug('%s \n GameServer stopping...' % str(stop_reason))

            self.server.stop('gameserver.stop')
            self.game.stop()

            if self.server.is_alive():
                debug ('waiting for socket-server process')
                self.server.join()
            
            self.running = False


    def debug(self):
        count = len(self.r_times)
        if count:
            all_time = sum(self.r_times)
            m_time = all_time/count

            debug('median time %s/%s = %s' % (all_time, count, m_time))
            

        

    def start(self):
        debug('Running...')
        self.running = True

        signal.signal(signal.SIGINT, self.sigint)

        stop_reason = 'None'
        try:
            self.server.start()
            debug('GameServer running')
            t = time()
            while 1:
                if self.server.has_exceptions():
                    debug('error in SocketServer')
                    #stop_reason = list(self.server.get_exceptions())
                    break

                r_time = time()
            
                self.game_worker()
                
                self.r_times.append(time() - r_time)
                
                delta = time()-t
                timeout = SERVER_TIMER - delta if delta<SERVER_TIMER else 0
                t = time()
                sleep(timeout)
            debug('game loop end')

        # except:
        #     except_type, except_class, tb = exc_info()
        #     debug('exception!', except_type, except_class)
        #     for line in traceback.extract_tb(tb):
        #         debug(line)


        finally:
            debug('game loop exit')
         
            self.stop(stop_reason)
            
            
    



        

