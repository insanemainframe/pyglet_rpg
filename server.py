#!/usr/bin/env python
# -*- coding: utf-8 -*-
from game_lib.engine_lib import Player, Ball, GameObject
from game_lib.math_lib import Point
from game_lib.protocol_lib import *
from game_lib.server_lib import *
from game_lib.gui_lib import AskHostname

from random import randrange

from config import PROFILE, TILESIZE, HOSTNAME, BLOCKTILES

class GameServer(SocketServer, TimerCallable, GameObject, AskHostname):
    hostname = None
    player_list = []
    client_requestes = {}
    client_responses = {}
    ball_counter=0
    def __init__(self):
        AskHostname.__init__(self)
        EpollServer.__init__(self)
        TimerCallable.__init__(self)
        self.init()
    
    def timer_handler(self):
        #self.steps.update()
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
                if player.alive:
                    self.client_responses[client_name].append(('look',player.look()))
                else:
                    self.client_responses[client_name].append(('respawn',player.respawn()))
                    self.client_responses[client_name].append(('look',player.look()))
                    player.alive = True
                    
            else:
                #если объект не управляемый
                if player.lifetime:
                    player.go()
                    player.lifetime-=1
                else:
                    #если срок жизни кончился - убиваем
                    del self.players[player.name]
        
        
    def accept(self, client):
        "вызывается при подключении клиента"
        self.players[client] = Player(client, self.choice_position(), 7)
        self.client_requestes[client] = []
        self.client_responses[client] = []
        
        message = self.players[client].accept()
        message = pack(message, 'accept')
        
        self.put_message(client, message)
    
    
    
    def strike_ball(self,client_name, vector):
        name = 'ball%s' % self.ball_counter
        self.ball_counter+=1
        position = self.players[client_name].position
        self.players[name] = Ball(name, position, vector, client_name)


    def write(self, client):
        if self.client_responses[client]:
            for action, response in self.client_responses[client]:
                data = pack(response, action)
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

