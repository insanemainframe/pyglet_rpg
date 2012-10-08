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
        #self.create_monsters(5, Lych)
        #self.create_monsters(5, Ghast)
        self.create_monsters(5, Cat)
        
    
    def create_monsters(self, n, monster_type):
        for i in range(n):
            position = game.choice_position(monster_type, 30)
            monster = monster_type('monster%s' % self.monster_count, position)
            self.monster_count+=1
            game.new_object(monster)
            
    def game_connect(self, name):
        "создание нового игрока"
       
        position = game.choice_position(Player)
        new_player = Player(name, position , 7)
        game.new_object(new_player)
        #
        #уже существующие объекты
        message = (game.world.size, new_player.position)
        #оставляем сообщение о подключении
        print 'New player %s position %s' % (name, position)
        
        self.messages[name] = [('ServerAccept', message)]+ new_player.accept()
    
    
    
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
        active_locations = game.get_active_locations()
        self.active_players = []
        
        for location in active_locations:
            for player in location.players.values():
                self.active_players.append(player)
                player.update()
            
            for static_object in location.static_objects.values():
                static_object.update()

        game.clear_players()
        game.clear_static()
                    
        
    def game_responses(self):
        "получение ответов управляемых игрокв"
        #получаем ответы игроков
        for name, player in game.guided_players.items():
            if self.messages[name]:
                yield name, self.messages[name]
                self.messages[name] = []
            yield (name, player.handle_response())
    
    def end_round(self):
        "завершение игрового раунда"
        for player in self.active_players:
            DynamicObject.complete_round(player)
            player.complete_round()
                
        game.clear_events()
            
        
    

    
    def game_quit(self, name):
        print '%s quit' % name
        del self.messages[name]
        game.remove_object(name, True)
    
    def round_debug(self):
        if not game.guided_players:
            primary_activity = 0
            slavery_activity = 0
            for row in game.world.locations:
                for location in row:
                    if location.primary_activity:
                        print [player for player in location.players.values() if isinstance(player, ActiveState)]
                        raw_input('__\n')
                    primary_activity+=location.primary_activity
                    slavery_activity+=location.slavery_activity
            
            print "prim %s slav %s" % (primary_activity, slavery_activity)
    
    def debug(self):
        from collections import Counter
        counter = Counter()
        print 'len(game.players)',len(game.players)
        print 'len(game.guided_players)', len(game.guided_players)
        for player in game.players.values():
           counter[player.__class__.__name__]+=1
        
        print counter
                
    
    


if __name__ == '__main__':
	Game()

