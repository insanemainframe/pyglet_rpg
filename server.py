#!/usr/bin/env python
# -*- coding: utf-8 -*-
from game_lib.engine import Game
from game_lib.math_lib import Point
from game_lib.protocol_lib import *
from game_lib.server_lib import *
from game_lib.gui_lib import AskHostname

from random import randrange

from config import PROFILE, TILESIZE, HOSTNAME, BLOCKTILES

class GameServer(SocketServer, TimerCallable, Game, AskHostname):
    hostname = None
    client_requestes = {}
    client_responses = {}
    client_list = set()
    def __init__(self):
        AskHostname.__init__(self)
        EpollServer.__init__(self)
        TimerCallable.__init__(self)
        Game.__init__(self)
    
    def timer_handler(self):
        #print 'self.process_action()'
        self.process_action(self.client_requestes)
        self.client_requestes = {client: [] for client in self.client_list}
        #print 'self.detect_collisions()'
        self.detect_collisions()
        #print 'self.process_look()'
        look =  self.process_look()
        #print 'for name, messages in look.items()'
        for name, messages in look.items():
            self.client_responses[name].append(messages)
        

    def accept(self, client):
        "вызывается при подключении клиента"
        print 'accept'
        self.client_list.add(client)
        self.client_requestes[client] = []
        self.client_responses[client] = []
        message = ('accept', self.create_player(client))
        self.client_responses[client] = [message]
        print 'acepting complete'


    def write(self, client):
        if self.client_responses[client]:
            try:
                for action, response in self.client_responses[client]:
                    data = pack(response, action)
                    self.put_message(client, data)
            except Exception, excp:
                print 'server.writ eror %s \n %s' % (excp, str(self.client_responses[client][0]))
                raise excp
            finally:
                self.client_responses[client] = []
    
    def read(self, client, messages):
        for message in messages:
            request = unpack(message)
            self.client_requestes[client].append(request)

    
    def close(self, client):
        print 'server close %s' % str(client)
        self.client_list.remove(client)
        self.remove_object(client)
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
        print 'profile'
        import cProfile
        cProfile.run('main()', '/tmp/game_server.stat')
        

    else:
        main()

