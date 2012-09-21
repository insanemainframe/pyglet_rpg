#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from sys import path
path.append('../')

from game_lib.math_lib import *
from game_lib.map_lib import *
from game_lib.engine_lib import *
from game_lib import game
from game_lib.game_objects import *

from config import *

#####################################################################
class Game:
    "класс игры"
    def handle_connect(self, name):
        "создание нового игрока"
        position = game.choice_position(Player)
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
            #если это игрок, то выполняем его действия
            if isinstance(player, Guided):
                for action, message in messages[name]:
                    try:
                        player.handle_action(action, message)
                    except ActionDenied:
                        pass
            #если игрок не отправлял действий, то вызываем метод update
            update = player.update()
            if update:
                game.add_update(*update)
            #обрабатываем объекты с ограниченным сроком жизни
            if isinstance(player, Temporary):
                if not player.lifetime:
                    #если срок жизни кончился - убиваем
                    game.remove_object(name)
            #завершаем раунд для игрока
            player.complete_round()
    
    def handle_middle(self):
        "запускается между обработкой запросов и ответов"
        game.detect_collisions()
        game.clear()
        for player in game.players.values():
            if not player.alive:
                if isinstance(player, Respawnable):
                    player.respawn()
                    
            
    def handle_responses(self):
        "смотрим"
        messages = {}
        #подготавливаем обновления для выборочного обзора
        for name, player in game.players.items():
            if isinstance(player, Guided):
                messages[name] = player.handle_response()

        game.updates.clear()
        return messages
    
    
    
    def handle_quit(self, name):
        game.remove_object(name)
                
    
    


if __name__ == '__main__':
	Game()

