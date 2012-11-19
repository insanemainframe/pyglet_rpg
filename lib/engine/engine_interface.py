#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from config import *
from server_logger import debug

from share.game_protocol import NewLocation, ServerAccept

from engine.world.singleton import game

from engine.enginelib.meta import ActionDenied
from engine.enginelib.mutable import MutableObject
from engine.game_objects import Player


from time import time

#####################################################################
class GameEngine:
    "интерфейс к движку игры"

    def __init__(self, save_time):
        game.start()
        self.messages = {}

            
    def game_connect(self, name):
        "создание нового игрока"
        debug('New player %s' % name)

        #выбираем позицию для нового игрока
        chunk_cord = game.mainlocation.main_chunk.cord
        #создаем игрока
        new_player = Player(name)
        game.mainlocation.new_object(new_player, chunk_cord)
        game.guided_changed = True
        
        yield ServerAccept()

        for message in new_player.accept_response():
            yield message
        raise StopIteration

    def is_active(self):
        game.is_active()


    
    def game_requests(self, messages):
        "выполнение запросов игроков"
        for name, message_list in messages.items():
            if name in game.guided_players:
                player = game.guided_players[name]
                for action, message in message_list:
                    # debug ('action', action)
                    try:
                        player.handle_action(action, message)
                    except ActionDenied:
                        pass
    
    
    def game_update(self):
        "отыгрывание раунда игры"
        #debug ('update')
        
        #обновляем объекты в активных локациях
        cur_time = time()
        for chunk in game.get_active_chunks():
            chunk.update(cur_time)
            
            
        
        #обновляем активнеы локации
        for chunk in game.get_active_chunks():
            chunk.clear()

                    
        
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
            chunk.complete_round()
        
        game.guided_changed = False
        
       
    def save(self):
        game.save()

    def stop(self):
        debug('stopping engine')
        game.stop()


    def game_quit(self, name):
        debug('%s quit' % name)

        if name in self.messages:
            del self.messages[name]
        game.remove_guided(name)
        game.guided_changed = True
    
    
                