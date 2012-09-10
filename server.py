#!/usr/bin/env python
# -*- coding: utf-8 -*-
from engine_lib import *
from math_lib import Point
from protocol_lib import *
from server_lib import EpollServer, TimerCallable

from config import PROFILE

class GameServer(EpollServer, TimerCallable):
    def __init__(self):
        EpollServer.__init__(self)
        TimerCallable.__init__(self)
        self.games = {}
        self.player_list = []
        self.client_requestes = {}
        self.client_responses = {}
        self.new_objects = {}
        self.object_updates = {}
    
    def timer_handler(self):
        for client, game in self.games.items():
            try:
                vector = self.client_requestes[client].pop()
            except IndexError:
                vector = Point(0,0)
            #хдим, смотрим
            game.go(vector)
            looked = game.look()
            #оповещаем остальных о своих передвижениях
            self.alarm_updates(client, game.get_vector())
            #ищем новые объекты
            new_objects = {}
            for name, position in self.new_objects[client].items():
                if name!=client:
                    new_objects[name] = (position,'player')
            self.new_objects[client] = {}
            #ищем обновления объектов
            updates = self.object_updates[client] #{client: game.get_vector()}
            self.object_updates[client] = {}
            self.client_responses[client].append(looked + (new_objects, updates))
        
        
    def accept(self, client):
        "вызывается при подключении клиента"
        self.games[client] = Game(7)
        self.client_requestes[client] = []
        self.client_responses[client] = []
        self.new_objects[client] = {}
        self.object_updates[client] = {}
        
        accept_data = self.games[client].accept() + (self.get_objects(client),)
        message = pack_server_accept(*accept_data)
        print 'accept_data', type(message), len(message)
        
        self.alarm_new_object(client, self.games[client].get_position())
        self.put_message(client, message)
    
    def get_objects(self, client):
        new_objects = {}
        for name, game in self.games.items():
            new_objects[name]=(game.get_position(),'player')
        return new_objects
    
    def alarm_updates(self, name, vector):
        for client, update_dict in self.object_updates.items():
            #print "self.object_updates[%s][%s] = %s" % (client, name, vector)
            self.object_updates[client][name] = vector
    
    def alarm_new_object(self, client_name, position):
        for name, game in self.games.items():
            if name!=client_name:
                print 'elf.new_objects[%s[%s] %s' % (name, client_name, position)
                self.new_objects[name][client_name] = position
            


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
        del self.new_objects[client]
        del self.object_updates[client]

    
    def start(self):
        self.start_timer()
        self.run()


        

def main():
    server = GameServer()
    server.start()

if __name__ == '__main__':
    PROFILE = 0
    if PROFILE:
        import cProfile, pstats
        cProfile.run('main()', '/tmp/server_pyglet.stat')

    else:
        main()

