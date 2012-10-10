#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from sys import path
path.append('../')

from share.mathlib import *
from share.game_protocol import NewWorld

from engine.game import game
from engine.engine_lib import *
from engine.game_objects import Player


from config import *

#####################################################################
class GameEngine:
    "класс игры"
    monster_count = 0
    def __init__(self):
        game.start()
        self.messages = {}
            
    def game_connect(self, name):
        "создание нового игрока"
       
        position = game.choice_position(game.mainworld, Player)
        new_player = Player(name, game.mainworld, position , 7)
        #
        #уже существующие объекты
        #оставляем сообщение о подключении
        print 'New player %s position %s' % (name, position)
        
        world = new_player.world
        
        self.messages[name] = [NewWorld(world.name, world.size, new_player.position, world.background)]
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
            messages = []
            if self.messages[name]:
                messages += self.messages[name]
                self.messages[name] = []
            for response in player.handle_response():
                messages.append(response)
            
            yield name, messages


    def end_round(self):
        "завершение игрового раунда"
        for location in self.active_locations:
            for player in location.players.values():
                DynamicObject.complete_round(player)
                player.complete_round()
            location.complete_round()
        
       
                
    
    def game_quit(self, name):
        print '%s quit' % name
        del self.messages[name]
        game.remove_guided(name)
    
    
                
    
    


if __name__ == '__main__':
	Game()

