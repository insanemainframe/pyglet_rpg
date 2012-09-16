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

class Game(GameShare):
    updates = {}
    new_objects = {}
    ball_counter=0
    def __init__(self):
        GameShare.__init__(self)
    
    def create_player(self, name):
        position = self.choice_position()
        new_player = Player(name, position , 7)
        self.new_object(new_player)
        world_size = self.size
        #
        self.new_objects[name] = {}
        #обзор
        looked = new_player.look({})[0]
        observed = [(i,j) for (i,j), tilename in looked]
        tiles = [(Point(i,j), tilename) for ((i,j), tilename) in looked]
        #уже существующие объекты
        objects = {name:(player.position, 'self' if name==new_player.name else player.tilename)
                    for name, player in self.players.items()}
                
        return world_size, new_player.position, tiles, observed, objects, []
    
    def new_object(self, player):
        "ововестить всех о новом объекте"
        self.players[player.name] = player
        for name in self.players:
            if self.players[name].guided and player.name!=name:
                self.new_objects[name][player.name] = (player.position, player.tilename)
    
    def process_action(self, messages):
        "совершаем действия игроками, возвращает векторы игрокам и устанавливает обновления"
        for name, player in self.players.items():
            if player.guided:
                vector = Point(0,0)
                if messages[name]:
                    action, message = messages[name].pop()
                    if action=='move_message':
                         vector = message
                    elif action=='ball_message':
                        self.strike_ball(name, message)
                self.updates[name] = (player.position, player.go(vector), player.tilename)
            else:
                if player.lifetime:
                    self.updates[name] = (player.position, player.go(), player.tilename)
                    player.lifetime-=1
                else:
                    #если срок жизни кончился - убиваем
                    self.remove_object(name)
        
            #очищаем
    
    def process_look(self):
        "смотрим"
        messages = {}
        #подготавливаем обновления для выборочного обзора
        updates_for_look = {(position/TILESIZE).get():(name,(position, vector, tilename))
                            for name,(position, vector, tilename) in self.updates.items()}
        for name, player in self.players.items():
            if player.guided:
                messages[name] = []
                #если игрок умер - респавн
                if not player.alive:
                    old_position = player.position
                    vector, new_position = player.respawn()
                    messages[name].append(('respawn', new_position))
                    self.updates[name] = (old_position, vector, player.tilename)
                    player.alive = True
                #новые для игрока объекты
                new_objects = self.new_objects[name]
                self.new_objects[name] = {}
                #смотрим карту
                #if player.prev_position == player.position:
                #    new_looked = []
                #    
                #else:
                looked, updates = player.look(updates_for_look)
                observed = [(i,j) for (i,j), tilename in looked]
                new_looked = looked  - player.prev_looked
                new_looked = [(Point(i,j),tilename) for (i,j), tilename in new_looked]
                player.prev_looked = looked
                #ветор движения на этом ходе
                move_vector = player.move_vector
                
                message = (move_vector, new_looked, observed, new_objects, updates, [])
                messages[name].append(('look', message))
        self.updates = {}
        return messages
    
    def detect_collisions(self):
        for Name, Player in self.players.items():
            for name, player in self.players.items():
                if name!=Name:
                    distance = abs(Player.position - player.position)
                    if distance <= Player.radius+player.radius:
                        if Player.mortal and player.human and player.name!=Player.striker:
                            print 'colission'
                            player.alive = False
                
    def clean(self):
        for name in self.players:
            if hasattr(self.players[name], REMOVE):
                if self.players[name].REMOVE:
                    self.remove_object(name)
    
    def strike_ball(self,player_name, vector):
        ball_name = 'ball%s' % self.ball_counter
        self.ball_counter+=1
        player_position = self.players[player_name].position
        ball = Ball(ball_name, player_position, vector, player_name)
        self.new_object(ball)
    
    def remove_object(self,name):
        self.updates[name] = (self.players[name].position, 'remove', 'REMOVED')
        if self.players[name].guided:
            del self.new_objects[name]
        del self.players[name]


if __name__ == '__main__':
	Game()

