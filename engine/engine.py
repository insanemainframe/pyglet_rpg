#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from sys import path
path.append('../')

from share.mathlib import *
from share.map import *

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
        self.create_monsters(5, Ghast)
        self.create_monsters(5, Cat)
        
    
    def create_monsters(self, n, monster_type):
        for i in range(n):
            position = game.choice_position(monster_type, 15)
            monster = monster_type('monster%s' % self.monster_count, position)
            self.monster_count+=1
            game.new_object(monster)
            
    def game_connect(self, name):
        "создание нового игрока"
        print 'New player %s' % name
        position = game.choice_position(Player)
        new_player = Player(name, position , 7)
        game.new_object(new_player)
        world_size = game.size
        #
        #обзор
        looked, observed, events, static_objects, static_events = new_player.look()
        #уже существующие объекты
        message = (world_size, new_player.position, looked, observed, events, static_objects, static_events)
        #оставляем сообщение о подключении
        self.messages[name] = [('ServerAccept', message)]
    
    def game_requests(self, messages):
        "совершаем действия игроками, возвращает векторы игрокам и устанавливает обновления"
        for name, player in game.guided_players.items():     
            if name in messages:
                for action, message in messages[name]:
                        try:
                            player.handle_action(action, message)
                        except ActionDenied:
                            pass
    
    def game_middle(self):
        "запускается между обработкой запросов и ответов"
        for player in game.players.values():
            #если игрок не отправлял действий, то вызываем метод update
            player.update()
            #обрабатываем объекты с ограниченным сроком жизни
            if isinstance(player, Temporary):
                if not player.lifetime:
                    #если срок жизни кончился - убиваем
                    player.REMOVE = True
            #завершаем раунд для игрока
            player.complete_round()
        game.clear()

                    
            
    def game_responses(self):
        "смотрим"
        #подготавливаем обновления для выборочного обзора
        messages = {}
        for name, player in game.guided_players.items():
            messages[name] = self.messages[name]
            self.messages[name] = []
            messages[name].extend(player.handle_response())

        game.clear_events()
        return messages
    

    
    def game_quit(self, name):
        print '%s quit' % name
        del self.messages[name]
        game.remove_object(name, True)
                
    
    


if __name__ == '__main__':
	Game()

