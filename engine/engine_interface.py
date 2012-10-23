#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from share.mathlib import *
from share.game_protocol import NewWorld, ServerAccept

from engine.singleton import game
from engine.enginelib.meta import *
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
        #выбираем позицию для нового игрока
        position = game.mainworld.choice_position(Player, ask_player = True)
        #создаем игрока
        new_player = Player(name, position)
        game.mainworld.new_object(new_player)
        
        #оставляем сообщение о подключении
        self.messages[name] = []
        for message in new_player.accept_response():
            self.messages[name].append(message)
        
        game.guided_changed = True
        print('New player %s' % name)

        return ServerAccept()
    
    
    def game_requests(self, messages):
        "выполнение запросов игроков"
        for name, player in game.guided_players.items():     
            if name in messages:
                for action, message in messages[name]:
                        try:
                            player.handle_action(action, message)
                        except ActionDenied:
                            pass
    
    
    def game_update(self):
        "отыгрывание раунда игры"
        #получаем список активных локаций
        self.active_locations = game.get_active_locations()
        
        
        #обновляем объекты в активных локациях
        for location in self.active_locations:
            for player in location.players.values():
                player.update()
            
            for static_object in location.static_objects.values():
                static_object.update()
        
        #обновляем активнеы локации
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
            #завершаем раунд для объектов в локации
            for player in location.players.values():
                DynamicObject.complete_round(player)
                player.complete_round()
            location.complete_round()
        
        game.guided_changed = False
        
       
    def save(self):
        game.save()
    
    def game_quit(self, name):
        print('%s quit' % name)
        del self.messages[name]
        game.remove_guided(name)
        game.guided_changed = True
    
    
                