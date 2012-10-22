#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from config import SERVER_TIMER, HOSTNAME, PROFILE_SERVER, SERVER_PROFILE_FILE

from sys import exit as sys_exit, exc_info
import traceback
import cProfile
from time import time, sleep
from collections import defaultdict

from engine.engine_interface import GameEngine
from share.packer import pack, unpack
from share.ask_hostname import ask_hostname
from serverside.socket_server import SocketServer


save_time = 600

class GameServer(object):
    "игровой сервер"
    
    def __init__(self, hostname):
        self.server = SocketServer(hostname)

        self.client_list = set()    
        self.client_requestes = defaultdict(list)
        
        #сам игровой движок
        self.game = GameEngine(save_time)
        
        self.round_counter = 0
        self.r_times = []
            

    def game_worker(self):
        "обращается к движку по расписанию"
        #смотрим новых клиентов
        for client_name in self.server.get_accepted():
            accept_response = pack(self.game.game_connect(client_name))
            self.server.put_response(client_name, accept_response)
            self.client_list.add(client_name)
        
        #смотрим отключившихся клиентов
        for client_name in self.server.get_closed():
            self.game.game_quit(client_name)
            self.client_list.remove(client_name)
        
        #смотрим новые запросы и очищаем очередь
        
        for client, message in self.server.get_requestes():
            self.client_requestes[client].append(unpack(message))

        
        #отправляем запросы движку
        self.game.game_requests(self.client_requestes)
        self.client_requestes.clear()
        
        #обновляем движок
        self.game.game_update()
        
        #вставляем ответы в очередь на отправку
        for name, messages in self.game.game_responses():
            for message in messages:
                response = pack(message)
                self.server.put_response(name, response)
        
        #завершаем раунд игры
        self.game.end_round()


    def stop(self, stop_reason = ''):
        #считаем среднее время на раунд
        print('%s \n GameServer stopping...' % str(stop_reason))
        self.server.stop()
        count = len(self.r_times)
        if count:
            all_time = sum(self.r_times)
            m_time = all_time/count
            print('median time %s/%s = %s' % (all_time, count, m_time))
        if isinstance(stop_reason, BaseException):
            raise stop_reason
        

    def start(self):
        print('Running...')
        stop_reason = 'None'
        try:
            self.server.start()
            print('GameServer running')
            t = time()
            while 1:
                if not self.server.excp.empty():
                    print('error in SocketServer')
                    stop_reason = self.server.excp.get_nowait()
                    break

                r_time = time()
            
                self.game_worker()
                
                self.r_times.append(time() - r_time)
                
                delta = time()-t
                timeout = SERVER_TIMER - delta if delta<SERVER_TIMER else 0
                t = time()
                sleep(timeout)
            print('game loop end')

        except KeyboardInterrupt:
            stop_reason= 'KeyboardInterrupt'
            self.game.save()
            print('stop_reason:', stop_reason)

        except:
            except_type, except_class, tb = exc_info()
            print('exception!', except_type, except_class)
            for line in traceback.extract_tb(tb):
                print(line)


        finally:
            print('game loop exit')
         
            self.stop(stop_reason)
            sys_exit()
    



        

def main():
    hostname = ask_hostname(HOSTNAME)
    server = GameServer(hostname)
    server.start()

if __name__ == '__main__':
    if PROFILE_SERVER:
        print('profile')
        cProfile.run('main()', SERVER_PROFILE_FILE)
        
    else:
        main()

