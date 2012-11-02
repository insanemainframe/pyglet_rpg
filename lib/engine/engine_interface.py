#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from share.game_protocol import NewWorld, ServerAccept

from engine.singleton import game

from engine.enginelib.meta import Updatable,GameObject, ActionDenied

from engine.game_objects import Player


from config import *

#####################################################################
class GameEngine:
    "интерфейс к движку игры"
    monster_count = 0
    def __init__(self, save_time):
        game.start()
        self.messages = {}
            
    def game_connect(self, name):
        "создание нового игрока"
        print('New player %s' % name)

        #выбираем позицию для нового игрока
        position = game.mainworld.choice_position(Player, game.mainworld.main_chunk)
        #создаем игрока
        new_player = Player(name, position)
        game.mainworld.new_object(new_player)
        game.guided_changed = True
        
        yield ServerAccept()

        for message in new_player.accept_response():
            yield message
        
        
        

        
    
    
    def game_requests(self, messages):
        "выполнение запросов игроков"
        for name, message_list in messages.items():
            if name in game.guided_players:
                player = game.guided_players[name]
                for action, message in message_list:
                        try:
                            player.handle_action(action, message)
                        except ActionDenied:
                            pass
    
    
    def game_update(self):
        "отыгрывание раунда игры"
        #получаем список активных локаций
        self.active_chunks = game.get_active_chunks()
        
        
        #обновляем объекты в активных локациях
        for chunk in self.active_chunks:
            for player in chunk.get_list(Updatable):
                player.update()
            
        
        #обновляем активнеы локации
        for chunk in self.active_chunks:
            chunk.update()

                    
        
    def game_responses(self):
        "получение ответов управляемых игрокв"
        #получаем ответы игроков
        for name, player in game.guided_players.items():
            messages = []
            for response in player.handle_response():
                messages.append(response)
            
            yield name, messages


    def end_round(self):
        "завершение игрового раунда"
        for chunk in game.get_active_chunks():
            for player in chunk.get_list(Updatable):
                print 'end_Rouns', player.name
                GameObject.complete_round(player)
                player.complete_round()
                player.clear_events()
            chunk.complete_round()
        
        game.guided_changed = False
        
       
    def save(self):
        game.save()
    
    def game_quit(self, name):
        print('%s quit' % name)
        if name in self.messages:
            del self.messages[name]
        game.remove_guided(name)
        game.guided_changed = True
    
    
                