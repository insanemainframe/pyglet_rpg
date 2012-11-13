#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from share.mathlib cimport Point
from share.game_protocol import NewWorld, ServerAccept

from engine.world.singleton import game
from engine.enginelib.meta import DynamicObject
from engine.enginelib.movable import Movable

from engine.game_objects import Player


from config import *
from share.logger import print_log


#####################################################################
class GameEngine:
    "интерфейс к движку игры"
    monster_count = 0
    def __init__(self, save_time):
        game.start()
            
    def game_connect(self, str name):
        "создание нового игрока"
        cdef Point position

        #выбираем позицию для нового игрока
        position = game.mainworld.choice_position(Player, ask_player = True)
        #создаем игрока
        new_player = Player(name, position)
        game.mainworld.new_object(new_player)
        
        game.guided_changed = True
        print_log('New player %s' % name)

        #оставляем сообщение о подключении
        yield ServerAccept()
        for accept_response in new_player.accept_response():
            yield accept_response
        
        

        
    
    
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
                if isinstance(player, Movable):
                    player._update_move()
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
            messages = [response for response in player.handle_response()]
            
            yield name, messages


    def end_round(self):
        "завершение игрового раунда"
        for location in self.active_locations:
            #завершаем раунд для объектов в локации
            for player in location.players.values():
                if isinstance(player, Movable):
                    player._complete_move()
                
                if isinstance(player, DynamicObject):
                    DynamicObject._complete_round(player)

            location.complete_round()
        
        game.guided_changed = False
        
       
    def save(self):
        game.save()
    
    def game_quit(self, name):
        print_log('%s quit' % name)
        game.remove_guided(name)

        game.guided_changed = True
    
    
                