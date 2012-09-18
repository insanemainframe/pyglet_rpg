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
    
    def create_player(self, name):
        "создание нового игрока"
        position = game.choice_position()
        new_player = Player(name, position , 7)
        game.new_object(new_player)
        world_size = game.size
        #
        #обзор
        looked, observed, updates = new_player.look()
        #уже существующие объекты
                
        return world_size, new_player.position, looked, observed, updates, []
    
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
        self.detect_collisions()
            
    def handle_responses(self):
        "смотрим"
        messages = {}
        #подготавливаем обновления для выборочного обзора
        for name, player in game.players.items():
            if player.guided:
                messages[name] = []
                #если игрок умер - респавн
                if not player.alive:
                    message, update = player.respawn()
                    messages[name].append(message)
                    game.add_update(*update)
                    player.alive = True
                #смотрим карту
                new_looked, observed, updates = player.look()
                #ветор движения на этом ходе
                move_vector = player.move_vector
                
                message = (move_vector, new_looked, observed, updates, [])
                messages[name].append(('look', message))
        
        game.updates.clear()
        return messages
    
    def detect_collisions(self):
        "определяем коллизии"
        for Name, Player in game.players.items():
            for name, player in game.players.items():
                if name!=Name:
                    distance = abs(Player.position - player.position)
                    if distance <= Player.radius+player.radius:
                        if Player.mortal and player.human and player.name!=Player.striker:
                            print 'colission'
                            player.alive = False
    
    def handle_quit(self, name):
        game.remove_object(name)
                
    def clean(self):
        "удаляем объекты отмеченыне меткой REMOVE"
        for name in game.players:
            if hasattr(game.players[name], REMOVE):
                if game.players[name].REMOVE:
                    game.remove_object(name)
    
    


if __name__ == '__main__':
	Game()

