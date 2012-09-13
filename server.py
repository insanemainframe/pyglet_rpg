#!/usr/bin/env python
# -*- coding: utf-8 -*-
from game_lib.engine_lib import Player, Ball, GameObject
from game_lib.math_lib import Point
from game_lib.protocol_lib import *
from game_lib.server_lib import EpollServer, TimerCallable
from game_lib.gui_lib import AskHostname

from config import PROFILE, TILESIZE, HOSTNAME

class GameServer(EpollServer, TimerCallable, GameObject, AskHostname):
    hostname = None
    def __init__(self):
        AskHostname.__init__(self)
        EpollServer.__init__(self)
        TimerCallable.__init__(self)
        self.player_list = []
        self.client_requestes = {}
        self.client_responses = {}
        self.init()
        self.ball_counter=0
    
    def timer_handler(self):
        for client_name, player in self.players.items():
            if player.guided:
                #обрабатываем управляемые объекты(игроков)
                if len(self.client_requestes[client_name])>0:
                    action, vector = self.client_requestes[client_name].pop()
                    #ходим, смотрим
                    if action=='move_message':
                        player.go(vector)
                    elif action=='ball_message':
                        self.strike_ball(client_name, vector)
                else:
                    player.go()
                self.client_responses[client_name].append(player.look())
            else:
                #
                if player.lifetime:
                    player.go()
                    player.lifetime-=1
                else:
                    del self.players[player.name]
        
        
    def accept(self, client):
        "вызывается при подключении клиента"
        #player_position = Point(randrange(self.size)*TILESIZE-look_size,randrange(self.size)*TILESIZE-look_size)
        player_position = Point(GameObject.size*TILESIZE/2, GameObject.size*TILESIZE/2)
        self.players[client] = Player(client, player_position,7)
        self.client_requestes[client] = []
        self.client_responses[client] = []
        
        message = pack(self.players[client].accept(),'accept')
        
        self.put_message(client, message) 
    
    def strike_ball(self,client_name, vector):
        name = 'ball%s' % self.ball_counter
        self.ball_counter+=1
        position = self.players[client_name].position
        self.players[name] = Ball(name, position, vector)


    def write(self, client):
        if self.client_responses[client]:
            for response in self.client_responses[client]:
                data = pack(response, 'server_message')
                self.put_message(client, data)
            self.client_responses[client] = []
    
    def read(self, client, messages):
        for message in messages:
            request = unpack(message)
            self.client_requestes[client].append(request)
    
    def close(self, client):
        del self.players[client]
        del self.client_requestes[client]
        del self.client_responses[client]


    
    def start(self):
        self.start_timer()
        self.run()


        

def main():
    server = GameServer()
    server.start()

if __name__ == '__main__':
    if PROFILE:
        print 'profile'
        import cProfile
        cProfile.run('main()', '/tmp/game_server.stat')
        

    else:
        main()

