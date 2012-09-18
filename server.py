#!/usr/bin/env python
# -*- coding: utf-8 -*-
from game_lib.engine import Game
from game_lib.protocol_lib import pack, unpack
from game_lib.server_lib import SocketServer
from game_lib.ask_hostname import AskHostname


from config import PROFILE_SERVER, HOSTNAME
from game_lib.logger import SERVERLOG as LOG


class GameServer(SocketServer, Game, AskHostname):
    hostname = None
    client_requestes = {}
    client_responses = {}
    client_list = set()
    def __init__(self):
        AskHostname.__init__(self, HOSTNAME)
        SocketServer.__init__(self)
    
    def timer_handler(self):
        self.handle_requests(self.client_requestes)
        self.client_requestes = {client: [] for client in self.client_list}
        self.handle_middle()
        look =  self.handle_responses()
        for name, messages in look.items():
            responses = [pack(response, action) for action, response in messages]
            self.put_messages(name, responses)
        self.handle_write()
        return True
        

    def accept(self, client):
        "вызывается при подключении клиента"
        print 'accept player %s' % client
        self.client_list.add(client)
        self.client_requestes[client] = []
        self.client_responses[client] = []
        message = pack(*self.handle_connect(client))
        self.put_messages(client, [message])

    
    def read(self, client, message):
        if message:
            request = unpack(message)
            self.client_requestes[client].append(request)
    
    def close(self, client):
        print 'server close %s' % str(client)
        self.client_list.remove(client)
        self.handle_quit(client)
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

