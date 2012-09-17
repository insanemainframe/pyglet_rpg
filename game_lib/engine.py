#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Без имени.py
from sys import path
path.append('../')

from game_lib.math_lib import *
from game_lib.map_lib import *
from game_lib.engine_lib import *


from config import *
from game_lib.logger import ENGINELOG as LOG

#####################################################################
class Game(GameShare):
    "класс игры"
    ball_counter=0
    def __init__(self):
        GameShare.__init__(self)
    
    def create_player(self, name):
        "создание нового игрока"
        position = self.choice_position()
        new_player = Player(name, position , 7)
        self.new_object(new_player)
        world_size = self.size
        #
        #обзор
        looked, observed, updates = new_player.look()
        #уже существующие объекты
                
        return world_size, new_player.position, looked, observed, updates, []
    
    def new_object(self, player):
        "ововестить всех о новом объекте"
        self.players[player.name] = player
        #добавляем обновление
        key = (player.position/TILESIZE).get()
        update = (player.name, (player.position, player.move_vector, player.tilename))
        self.add_update(player.name, player.position, player.move_vector, player.tilename)
    
    def process_action(self, messages):
        "совершаем действия игроками, возвращает векторы игрокам и устанавливает обновления"
        for name, player in self.players.items():
            #если это игрок
            if player.guided:
                vector = Point(0,0)
                if messages[name]:
                    action, message = messages[name].pop()
                    if action=='move':
                         vector = message
                    elif action=='ball':
                        self.strike_ball(name, message)
                self.add_update(*player.go(vector))
            else:
                if player.lifetime:
                    self.add_update(*player.go())
                    player.lifetime-=1
                else:
                    #если срок жизни кончился - убиваем
                    self.remove_object(name)
        
            #очищаем
    
    def process_look(self):
        "смотрим"
        messages = {}
        #подготавливаем обновления для выборочного обзора
        for name, player in self.players.items():
            if player.guided:
                messages[name] = []
                #если игрок умер - респавн
                if not player.alive:
                    vector, new_position = player.respawn()
                    messages[name].append(('respawn', new_position))
                    self.add_update(name,player.position, vector, player.tilename)
                    player.alive = True
                #смотрим карту
                new_looked, observed, updates = player.look()
                #ветор движения на этом ходе
                move_vector = player.move_vector
                
                message = (move_vector, new_looked, observed, updates, [])
                messages[name].append(('look', message))
        
        self.updates.clear()
        return messages
    
    def detect_collisions(self):
        "определяем коллизии"
        for Name, Player in self.players.items():
            for name, player in self.players.items():
                if name!=Name:
                    distance = abs(Player.position - player.position)
                    if distance <= Player.radius+player.radius:
                        if Player.mortal and player.human and player.name!=Player.striker:
                            print 'colission'
                            player.alive = False
                
    def clean(self):
        "удаляем объекты отмеченыне меткой REMOVE"
        for name in self.players:
            if hasattr(self.players[name], REMOVE):
                if self.players[name].REMOVE:
                    self.remove_object(name)
    
    def strike_ball(self,player_name, vector):
        "игрока стреляет снарядом"
        ball_name = 'ball%s' % self.ball_counter
        self.ball_counter+=1
        player_position = self.players[player_name].position
        ball = Ball(ball_name, player_position, vector, player_name)
        self.new_object(ball)
    
    def remove_object(self,name):
        player = self.players[name]
        self.add_update(player.name, player.prev_position, 'remove', 'REMOVED')
        del self.players[name]


if __name__ == '__main__':
	Game()

