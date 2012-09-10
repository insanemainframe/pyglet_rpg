#!/usr/bin/env python
# -*- coding: utf-8 -*-
from engine_lib import Player, GameObject
from math_lib import Point
from protocol_lib import *
from server_lib import EpollServer, TimerCallable

from config import PROFILE, TILESIZE

class GameServer(EpollServer, TimerCallable):
    def __init__(self):
        EpollServer.__init__(self)
        TimerCallable.__init__(self)
        self.games = {}
        self.player_list = []
        self.client_requestes = {}
        self.client_responses = {}
        GameObject.init()
    
    def timer_handler(self):
        for client, game in self.games.items():
            try:
                vector = self.client_requestes[client].pop()
            except IndexError:
                vector = Point(0,0)
            #хдим, смотрим
            game.go(vector)
            self.client_responses[client].append(game.look())
        
        
    def accept(self, client):
        "вызывается при подключении клиента"
        #player_position = Point(randrange(self.size)*TILESIZE-look_size,randrange(self.size)*TILESIZE-look_size)
        player_position = Point(GameObject.size*TILESIZE/2, GameObject.size*TILESIZE/2)
        self.games[client] = Player(client, player_position,7)
        self.client_requestes[client] = []
        self.client_responses[client] = []
        
        message = pack_server_accept(*self.games[client].accept())
        print 'accept_data', type(message), len(message)
        
        self.put_message(client, message) 


    def write(self, client):
        if self.client_responses[client]:
            for response in self.client_responses[client]:
                data = pack_server_message(*response)
                self.put_message(client, data)
            self.client_responses[client] = []
    
    def read(self, client, messages):
        if messages:
            #print 'read', messages
            pass
        for message in messages:
            request = unpack_client_message(message)
            self.client_requestes[client].append(request)
    
    def close(self, client):
        del self.games[client]
        del self.client_requestes[client]
        del self.client_responses[client]


    
    def start(self):
        self.start_timer()
        self.run()


        

def main():
    server = GameServer()
    server.start()

if __name__ == '__main__':
    PROFILE = 1
    if PROFILE:
        import cProfile, pstats
        cProfile.run('main()', '/tmp/game_server.stat')
        stats = pstats.Stats('/tmp/game_server.stat')
        stats.sort_stats('cumulative')
        stats.print_stats()

    else:
        main()

