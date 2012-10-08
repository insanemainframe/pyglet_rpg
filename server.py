#!/usr/bin/env python
# -*- coding: utf-8 -*-
from engine.game_engine import GameEngine
from share.protocol_lib import Packer
from share.ask_hostname import AskHostname
from serverside.server_lib import SocketServer

from config import PROFILE_SERVER, HOSTNAME
from share.logger import SERVERLOG as LOG

from threading import RLock

class GameServer(SocketServer, AskHostname, Packer):
    hostname = None
    client_requestes = {}
    client_responses = {}
    client_list = set()
    
    def __init__(self):
        AskHostname.__init__(self, HOSTNAME)
        SocketServer.__init__(self)
        Packer.__init__(self)
        
        self.new_clients_lock = RLock()
        self.new_clients = []
        
        self.closed_clients_lock = RLock()
        self.closed_clients = []
        
        
        self.server_lock = RLock()
        
        self.game = GameEngine()
            

    def timer_handler(self):
        "обращается к движку по расписанию"
        #смотрим новых клиентов
        with self.new_clients_lock:
            new_clients = self.new_clients
            self.new_clients = []
        if new_clients:
            for new_client in new_clients:
                self.game.game_connect(new_client)
        
        #смотрим отключившихся клиентов
        with self.closed_clients_lock:
            closed_clients = self.closed_clients
            self.closed_clients = []
        if closed_clients:
            for closed_client in closed_clients:
                self.game.game_quit(closed_client)
        
        #смотрим новые запросы и очищаем очередь
        with self.server_lock:
            client_requestes = self.client_requestes
            self.client_requestes = {client: [] for client in self.client_list}
        
        #отправляем запросы движку
        self.game.game_requests(client_requestes)
        
        #обновляем движок
        self.game.game_middle()
        
        #вставляем ответы в очередь на отправку
        for name, messages in self.game.game_responses():
            self.write(name, messages)
        
        #завершаем раунд игры
        self.game.end_round()
        
        
    
    def write(self, name, responses):
        responses = [self.pack(response) for response in responses]
        self.put_messages(name, responses)
    
    #поток сервера
    def accept(self, client):
        "вызывается при подключении клиента"
        print 'accept client %s' % client
        with self.server_lock:
            self.client_list.add(client)
            self.client_requestes[client] = []
            self.client_responses[client] = []
        
        with self.new_clients_lock:
            self.new_clients.append(client)
        
    
    #поток движка
    def read(self, client, message):
        request = self.unpack(message)
        with self.server_lock:
            self.client_requestes[client].append(request)
    
    #поток сервера
    def close(self, client):
        self.client_list.remove(client)
        with self.closed_clients_lock:
           self.closed_clients.append(client)
        
        with self.server_lock:
            del self.client_requestes[client]
            del self.client_responses[client]

    def start(self):
        self.run()
    



        

def main():
    server = GameServer()
    server.start()

if __name__ == '__main__':
    if PROFILE_SERVER:
        print 'profile'
        import cProfile
        cProfile.run('main()', '/tmp/game_server.stat')
        

    else:
        main()

