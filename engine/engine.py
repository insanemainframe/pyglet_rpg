#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from sys import path
path.append('../')

from share.mathlib import *
from share.map import *

import game
from engine_lib import *
from game_objects import *

from config import *

#####################################################################
class Game:
    "класс игры"
    monster_count = 0
    def __init__(self):
        self.create_monsters(10, Zombie)
        self.create_monsters(5, Lych)
        self.create_monsters(5, Ghast)
        
    
    def create_monsters(self, n, monster_type):
        for i in range(n):
            position = game.choice_position(monster_type, 15)
            monster = monster_type('monster%s' % self.monster_count, position)
            self.monster_count+=1
            game.new_object(monster)
            
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
        message = (world_size, new_player.position, looked, observed, updates, [])
        return (message, 'ServerAccept')
    
    def handle_requests(self, messages):
        "совершаем действия игроками, возвращает векторы игрокам и устанавливает обновления"
        for name, player in game.guided_players.items():            
            for action, message in messages[name]:
                    try:
                        player.handle_action(action, message)
                    except ActionDenied:
                        pass
    
    def handle_middle(self):
        "запускается между обработкой запросов и ответов"
        for player in game.players.values():
            #player = game.players[name]
            #если игрок не отправлял действий, то вызываем метод update
            event = player.update()
            if event:
                game.add_event(*event)
            #обрабатываем объекты с ограниченным сроком жизни
            if isinstance(player, Temporary):
                if not player.lifetime:
                    #если срок жизни кончился - убиваем
                    player.REMOVE = True
            #завершаем раунд для игрока
            player.complete_round()
        game.clear()

                    
            
    def handle_responses(self):
        "смотрим"
        messages = {}
        #подготавливаем обновления для выборочного обзора
        for name, player in game.guided_players.items():
            messages[name] = player.handle_response()

        game.updates.clear()
        return messages
    
    def detect_collisions(self):
        "определяем коллизии"
        for Name, Player in game.players.items():
            for name, player in game.players.items():
                if name!=Name:
                    distance = abs(Player.position - player.position)
                    if distance <= Player.radius+player.radius:
                        if isinstance(Player, Mortal) and isinstance(player,Human):
                            if player.fraction!=Player.fraction:
                                player.hit(Player.damage)
                                if isinstance(Player, Fragile):
                                    Player.REMOVE = True
    
    def handle_quit(self, name):
        game.remove_object(name, True)
                
    
    


if __name__ == '__main__':
	Game()

