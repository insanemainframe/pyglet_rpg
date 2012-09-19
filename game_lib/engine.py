#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Без имени.py
from sys import path
path.append('../')

from game_lib.math_lib import *
from game_lib.map_lib import *
from game_lib.engine_lib import *
from game_lib import game

from config import *
from game_lib.logger import ENGINELOG as LOG

#####################################################################
class Game:
    "класс игры"
    def handle_connect(self, name):
        "создание нового игрока"
        position = game.choice_position()
        new_player = Player(name, position , 7)
        game.new_object(new_player)
        world_size = game.size
        #
        #обзор
        looked, observed, updates = new_player.look()
        #уже существующие объекты
                
        return (world_size, new_player.position, looked, observed, updates, []), 'server_accept'
    
    def handle_requests(self, messages):
        "совершаем действия игроками, возвращает векторы игрокам и устанавливает обновления"
        for name, player in game.players.items():
            #если это игрок
            if player.guided:
                for action, message in messages[name]:
                    try:
                        if action=='move':
                            vector = message
                            game.add_update(*player.go(vector))
                        elif action=='ball':
                            player.strike_ball(message)
                    except ActionDenied:
                        pass
                #если игрока не двигался то двигаемся с нулевым вектором
                if not player.moved:
                    vector = Point(0,0)
                    game.add_update(*player.go(vector))
            else:
                if player.lifetime:
                    game.add_update(*player.go())
                    player.lifetime-=1
                else:
                    #если срок жизни кончился - убиваем
                    game.remove_object(name)
            #завершаем раунд для игрока
            player.complete_round()
    
    def handle_middle(self):
        "запускается между обработкой запросов и ответов"
        game.detect_collisions()
        game.clear()
            
    def handle_responses(self):
        "смотрим"
        messages = {}
        #подготавливаем обновления для выборочного обзора
        for name, player in game.players.items():
            if player.guided:
                messages[name] = []
                #если игрок умер - респавн
                if not player.alive:
                    message, update1, update2 = player.respawn()
                    messages[name].append(message)
                    game.add_update(*update1)
                    game.add_update(*update2)
                    player.alive = True
                #смотрим карту
                new_looked, observed, updates = player.look()
                #ветор движения на этом ходе
                move_vector = player.move_vector
                
                message = (move_vector, new_looked, observed, updates, [])
                messages[name].append(('look', message))
        
        game.updates.clear()
        return messages
    
    
    
    def handle_quit(self, name):
        game.remove_object(name)
                
    
    


if __name__ == '__main__':
	Game()

