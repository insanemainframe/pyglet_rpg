#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from sys import path
path.append('../')

from share.mathlib import *
from share.game_protocol import ServerAccept

from game import game
from engine_lib import *
from game_objects import *

from config import *

#####################################################################
class GameEngine:
    "класс игры"
    monster_count = 0
    def __init__(self):
        self.messages = {}
        self.create_monsters(10, Zombie)
        self.create_monsters(5, Lych)
        #self.create_monsters(5, Ghast)
        self.create_monsters(5, Cat)
        
    
    def create_monsters(self, n, monster_type):
        for i in range(n):
            position = game.choice_position(monster_type, 30)
            name = monster_type.__name__
            monster = monster_type('%s_%s' % (name, self.monster_count) , position)
            self.monster_count+=1
            
    def game_connect(self, name):
        "создание нового игрока"
       
        position = game.choice_position(Player)
        new_player = Player(name, position , 7)
        game.new_object(new_player)
        #
        #уже существующие объекты
        #оставляем сообщение о подключении
        print 'New player %s position %s' % (name, position)
        
        self.messages[name] = [ServerAccept(game.world.size, new_player.position)]
        for message in new_player.accept_response():
            self.messages[name].append(message)
    
    
    
    def game_requests(self, messages):
        "выполнение запросов игроков"
        for name, player in game.guided_players.items():     
            if name in messages:
                for action, message in messages[name]:
                        try:
                            player.handle_action(action, message)
                        except ActionDenied:
                            pass
    
    
    def game_middle(self):
        "отыгрывание раунда игры"
        self.active_locations = game.get_active_locations()
        self.active_players = []
        
        for location in self.active_locations:
            for player in location.players.values():
                player.update()
            
            for static_object in location.static_objects.values():
                static_object.update()
        
        for location in self.active_locations:
            location.update()

                    
        
    def game_responses(self):
        "получение ответов управляемых игрокв"
        #получаем ответы игроков
        for name, player in game.guided_players.items():
            if self.messages[name]:
                yield name, self.messages[name]
                self.messages[name] = []
            for response in player.handle_response():
                yield (name, [response])


    def end_round(self):
        "завершение игрового раунда"
        for location in self.active_locations:
            for player in location.players.values():
                DynamicObject.complete_round(player)
                player.complete_round()
        
        for location in self.active_locations:
            location.complete_round()
                
            
    
    def game_quit(self, name):
        print '%s quit' % name
        del self.messages[name]
        game.remove_guided(name)
    
    
                
    
    


if __name__ == '__main__':
	Game()

